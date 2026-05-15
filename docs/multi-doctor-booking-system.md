# DentNav — Multi-Doctor Consultation Booking System

> **Scope:** Full redesign of the services / bookings / payments layer to support
> multiple doctors, per-doctor Calendly PAT integration, PostgreSQL-native slot
> locking (no Redis), and a complete Razorpay checkout flow.
>
> Supersedes the single-doctor sections of `payment-integration.md`.

---

## 0. Summary of Breaking Changes from v1 Design

| v1 | v2 (this doc) |
|---|---|
| `services.slug` | → `services.service_key` (migration 0011 — stable machine key, not a URL segment) |
| `services.category` | → **removed** (derived from `duration_minutes IS NULL`) |
| `services.calendly_event_type_uuid` | → **removed** from services; moved to `doctor_services` |
| Single global Calendly token | → per-doctor PAT stored in `doctors` table |
| Redis slot lock (5 min) | → PostgreSQL `slot_reservations` table with conditional upsert |
| No doctor concept | → `doctors` + `doctor_services` junction table |
| `bookings.service_id` only | → `bookings.doctor_service_id` (captures doctor + service in one FK) |
| Frontend fetches services via API | → **static** — `NEXT_PUBLIC_SERVICE_KEY_*` env vars, no page-load API call |

---

## 1. Database Schema

### 1.1 `services` (refactored)

Represents a **business product** — independent of any doctor or Calendly account.

```sql
CREATE TABLE services (
  id               VARCHAR(36)   PRIMARY KEY,          -- UUID v4
  service_key      VARCHAR(100)  UNIQUE NOT NULL,       -- machine key: 'visa_consultation'
  name             VARCHAR(255)  NOT NULL,              -- display: 'Visa Consultation'
  description      TEXT          NOT NULL DEFAULT '',
  duration_minutes INTEGER,                             -- NULL → analysis (no calendar)
  base_amount      INTEGER       NOT NULL,              -- minor unit (cents)
  currency         VARCHAR(10)   NOT NULL DEFAULT 'usd',
  is_active        BOOLEAN       NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ   NOT NULL DEFAULT now()
);
```

**What changed and why:**

| Change | Reason |
|---|---|
| `slug` → `service_key` | `slug` implies a URL segment. This is a machine lookup key used in backend logic and seeds — `service_key` says exactly that. |
| `category` removed | Was always derivable: `duration_minutes IS NULL` ↔ analysis; `duration_minutes IS NOT NULL` ↔ consultation. A boolean flag for two states adds no value. |
| `calendly_event_type_uuid` removed | Was a global single-doctor assumption. Now lives in `doctor_services` per doctor. |
| `amount` → `base_amount` | Signals it's the default price; doctors can override it in `doctor_services`. |

**Seed data:**

```sql
INSERT INTO services (id, service_key, name, duration_minutes, base_amount, currency) VALUES
  (gen_random_uuid(), 'analysis_access',       'Analysis Access',           NULL, 0, 'usd'),
  (gen_random_uuid(), 'intro_consultation',    'Introductory Consultation',   45, 0, 'usd'),
  (gen_random_uuid(), 'visa_consultation',     'Visa Consultation',           60, 0, 'usd'),
  (gen_random_uuid(), 'interview_preparation', 'Interview Preparation',       60, 0, 'usd'),
  (gen_random_uuid(), 'cv_sop_review',         'CV / SOP Review',             60, 0, 'usd'),
  (gen_random_uuid(), 'caapid_assistance',     'CAAPID Assistance',           60, 0, 'usd'),
  (gen_random_uuid(), 'license_guidance',      'License Guidance',            60, 0, 'usd');
```

---

### 1.2 `doctors` (new)

One row per consulting doctor on the platform.

```sql
CREATE TABLE doctors (
  id                  VARCHAR(36)   PRIMARY KEY,        -- UUID v4
  name                VARCHAR(255)  NOT NULL,
  bio                 TEXT          NOT NULL DEFAULT '',
  photo_url           TEXT          NOT NULL DEFAULT '',
  specializations     TEXT[]        NOT NULL DEFAULT '{}', -- e.g. ['visa','residency']
  calendly_user_uri   VARCHAR(512),                     -- e.g. https://api.calendly.com/users/XXXX
                                                        -- populated after first sync
  calendly_pat        TEXT,                             -- Personal Access Token (ENCRYPT AT REST)
  is_active           BOOLEAN       NOT NULL DEFAULT TRUE,
  created_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ   NOT NULL DEFAULT now()
);
```

**Notes on `calendly_pat`:**
- Each doctor has their own Calendly account and PAT. No shared global token.
- The PAT is used only server-side to call `api.calendly.com` on behalf of that doctor.
- **Must be encrypted at rest** (AES-256 via application-layer encryption or a secrets manager). Never log, never return via API.
- `calendly_user_uri` is fetched once via `GET /users/me` using the PAT and cached here so availability lookups don't need an extra round-trip.

---

### 1.3 `doctor_services` (new)

Junction table connecting a doctor to a service they offer, with their specific Calendly event type.

```sql
CREATE TABLE doctor_services (
  id                       VARCHAR(36)   PRIMARY KEY,   -- UUID v4
  doctor_id                VARCHAR(36)   NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
  service_id               VARCHAR(36)   NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
  calendly_event_type_uuid VARCHAR(255)  NOT NULL,      -- UUID from Calendly event type URI
  calendly_event_type_uri  TEXT          NOT NULL,      -- full URI: https://api.calendly.com/event_types/UUID
  price_override           INTEGER,                     -- NULL → use services.base_amount
  is_active                BOOLEAN       NOT NULL DEFAULT TRUE,
  created_at               TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_at               TIMESTAMPTZ   NOT NULL DEFAULT now(),

  CONSTRAINT uq_doctor_service UNIQUE (doctor_id, service_id)
);

CREATE INDEX ix_doctor_services_service_id ON doctor_services(service_id);
CREATE INDEX ix_doctor_services_doctor_id  ON doctor_services(doctor_id);
```

**Key design decisions:**

| Decision | Reasoning |
|---|---|
| `UNIQUE(doctor_id, service_id)` | One doctor can only offer a given service through one Calendly event type. If they need two (e.g. different durations for the same label), create two `services` rows. |
| `price_override` | Allows a doctor to charge more/less than the base price. Backend uses `COALESCE(ds.price_override, s.base_amount)` to resolve the effective price. |
| `calendly_event_type_uri` stored in full | Calendly APIs accept and return the full URI. Storing it avoids reconstructing it from the UUID repeatedly. |
| `ON DELETE RESTRICT` for service_id | Prevents removing a service while doctors are still offering it — safer than CASCADE (which would silently delete bookings). |

---

### 1.4 `slot_reservations` (new — replaces Redis TTL lock)

Holds a soft reservation for a slot the user has selected but not yet paid for. The 5-minute TTL is enforced via `expires_at` — no daemon or Redis needed.

```sql
CREATE TABLE slot_reservations (
  id                VARCHAR(36)   PRIMARY KEY DEFAULT gen_random_uuid(),
  doctor_service_id VARCHAR(36)   NOT NULL REFERENCES doctor_services(id) ON DELETE CASCADE,
  slot_time         TIMESTAMPTZ   NOT NULL,
  user_id           VARCHAR(36)   NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  expires_at        TIMESTAMPTZ   NOT NULL,  -- now() + 5 minutes
  created_at        TIMESTAMPTZ   NOT NULL DEFAULT now(),

  -- Only one active reservation per slot per doctor-service combination.
  -- This is the atomicity guarantee. The conditional upsert below exploits it.
  CONSTRAINT uq_slot_reservation UNIQUE (doctor_service_id, slot_time)
);

CREATE INDEX ix_slot_reservations_user_id    ON slot_reservations(user_id);
CREATE INDEX ix_slot_reservations_expires_at ON slot_reservations(expires_at);
```

**How the lock works (no Redis, no advisory locks):**

The UNIQUE constraint on `(doctor_service_id, slot_time)` gives us the atomicity.
The race-condition-proof insert is a conditional upsert:

```sql
-- Atomically claim a slot. Succeeds only if:
--   (a) no reservation exists for this slot, OR
--   (b) the existing reservation has expired
INSERT INTO slot_reservations (id, doctor_service_id, slot_time, user_id, expires_at)
VALUES (gen_random_uuid(), $ds_id, $slot_time, $user_id, now() + interval '5 minutes')
ON CONFLICT (doctor_service_id, slot_time) DO UPDATE
  SET user_id    = EXCLUDED.user_id,
      expires_at = EXCLUDED.expires_at
  WHERE slot_reservations.expires_at <= now()   -- ← only overwrite if expired
RETURNING id;
```

- If `RETURNING` is empty → slot is currently held by another user → respond 409.
- If `RETURNING` has a row → reservation created (or refreshed over an expired one).
- Two concurrent requests for the same slot race on the UNIQUE constraint.
  PostgreSQL serialises them: one wins (gets `RETURNING id`), the other gets
  nothing (the WHERE clause on DO UPDATE fails because `expires_at > now()` now).

**No cleanup daemon required.** Expired rows are invisible (queries filter `expires_at > now()`). A periodic `DELETE FROM slot_reservations WHERE expires_at <= now()` can be run as a background task for housekeeping, but it is not on the critical path.

---

### 1.5 `bookings` (updated)

```sql
CREATE TABLE bookings (
  id                    VARCHAR(36)   PRIMARY KEY,       -- UUID v4
  user_id               VARCHAR(36)   NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
  doctor_service_id     VARCHAR(36)   NOT NULL REFERENCES doctor_services(id) ON DELETE RESTRICT,
  payment_id            VARCHAR(36)   REFERENCES payments(id),  -- NULL until payment succeeds
  status                VARCHAR(50)   NOT NULL DEFAULT 'pending_payment',
    -- pending_payment | confirmed | completed | cancelled | no_show
  slot_time             TIMESTAMPTZ,                     -- chosen slot (UTC)
  slot_expires_at       TIMESTAMPTZ,                     -- slot_time booking hold TTL (15 min)
  scheduled_at          TIMESTAMPTZ,                     -- confirmed by Calendly
  calendly_event_uri    TEXT,                            -- full event URI from Calendly
  calendly_invitee_uri  TEXT,                            -- invitee URI for cancellations
  notes                 TEXT,
  created_at            TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE INDEX ix_bookings_user_id           ON bookings(user_id);
CREATE INDEX ix_bookings_doctor_service_id ON bookings(doctor_service_id);
CREATE INDEX ix_bookings_status            ON bookings(status);
```

**Changes from v1:**

| Change | Why |
|---|---|
| `service_id` → `doctor_service_id` | A booking is always for a specific doctor + service pair. `doctor_service_id` captures both in one FK and gives us the Calendly event type without an extra join through services. |
| `calendly_event_id` → `calendly_event_uri` | Calendly APIs return full URIs. Storing the URI avoids reconstructing it and makes cancellation/lookup calls trivial. |
| `calendly_invitee_url` → `calendly_invitee_uri` | Consistency with Calendly's naming. |

**Status transitions:**
```
pending_payment ──► confirmed   (payment succeeded + Calendly event created)
                ──► cancelled   (payment failed | slot expired | user cancelled)
confirmed       ──► completed   (session done — admin marks)
confirmed       ──► cancelled   (user or admin cancels)
confirmed       ──► no_show     (user missed session)
```

---

### 1.6 `payments` (unchanged structure, updated references)

```sql
CREATE TABLE payments (
  id                    VARCHAR(36)   PRIMARY KEY,
  user_id               VARCHAR(36)   NOT NULL REFERENCES users(user_id),
  doctor_service_id     VARCHAR(36)   REFERENCES doctor_services(id),  -- NULL for analysis_access
  reference_id          VARCHAR(36),  -- analyses.id OR bookings.id
  razorpay_order_id     VARCHAR(255)  UNIQUE NOT NULL,
  razorpay_payment_id   VARCHAR(255)  UNIQUE,
  razorpay_signature    VARCHAR(512),
  amount                INTEGER       NOT NULL,   -- snapshot at order time
  currency              VARCHAR(10)   NOT NULL DEFAULT 'inr',
  status                VARCHAR(50)   NOT NULL DEFAULT 'pending',
    -- pending | succeeded | failed | expired | refunded
  metadata              JSONB         NOT NULL DEFAULT '{}',
  created_at            TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- Prevents double-charging for the same analysis unlock
CREATE UNIQUE INDEX uq_payments_analysis_succeeded
  ON payments (reference_id)
  WHERE doctor_service_id IS NULL AND status = 'succeeded';
```

---

### 1.7 `calendly_webhook_events` (optional — audit / replay buffer)

Stores raw Calendly webhook payloads for debugging, replay, and idempotency.

```sql
CREATE TABLE calendly_webhook_events (
  id             VARCHAR(36)   PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type     VARCHAR(100)  NOT NULL,  -- 'invitee.created' | 'invitee.canceled'
  calendly_uuid  VARCHAR(255)  NOT NULL,  -- unique ID from Calendly payload
  booking_id     VARCHAR(36)   REFERENCES bookings(id),
  payload        JSONB         NOT NULL,
  processed_at   TIMESTAMPTZ,             -- NULL = not yet processed
  created_at     TIMESTAMPTZ   NOT NULL DEFAULT now(),

  CONSTRAINT uq_calendly_event UNIQUE (calendly_uuid)  -- idempotency key
);
```

---

### 1.8 Full ID Relationship Map

```
doctors (D1: Dr. Priya Sharma)
  └── doctor_services (DS1: D1 + consultation_visa service, event_type=EVT_UUID)
        └── slot_reservations (SR1: DS1, slot=10:00, user=U1, expires=T+5min)
        └── bookings (B1: DS1, user=U1, status=pending_payment)
              └── payments (P1: user=U1, ds=DS1, ref=B1, status=pending)
                    └── razorpay_order_id = order_ABC
                          └── razorpay_payment_id = pay_XYZ

users (U1)
  └── analyses (A1) ← user_id = U1
  └── bookings (B1) ← user_id = U1
  └── payments (P1) ← user_id = U1
```

---

## 2. What Calendly Concepts Mean

### Event Type vs. Scheduled Event

| Concept | What it is | Analogy |
|---|---|---|
| **Event Type** | A template: "60-min Visa Consultation". Defines duration, availability rules, buffer times. | A "product" listing on a menu |
| **Scheduled Event** | An actual booked instance of an event type at a specific time with a specific invitee. | A "purchased item" |
| **Availability** | The open slots Calendly computes for a given event type based on the doctor's connected calendar + business hours + buffers. | The "in stock" indicator on a product |

### Why availability is event-type-specific

Calendly does **not** expose a global "is this doctor free at 10:00?" API. Availability is always computed per event type because:
- Different event types can have different working hours (e.g., intro calls only on weekdays 9–12)
- Buffer times differ per event type
- Padding and limits are event-type-specific

**You cannot ask:** "When is Dr. Priya free?"
**You must ask:** "When is the 'Visa Consultation' event type for Dr. Priya available?"

This is why `doctor_services` maps each service to a specific `calendly_event_type_uuid` per doctor. There is no generic doctor availability endpoint.

### How `doctor_services` connects business to Calendly

```
User sees: "Book a Visa Consultation with Dr. Priya"
                        ↓
Backend resolves: SELECT calendly_event_type_uri
                  FROM doctor_services
                  WHERE doctor_id = 'D1'
                    AND service_id = (SELECT id FROM services WHERE service_key = 'visa_consultation')
                        ↓
Calendly API: GET /event_type_available_times?event_type=<uri>&start_time=...&end_time=...
                        ↓
Returns: list of open slots specific to Dr. Priya's "Visa Consultation" event type
```

The `doctor_services` row is the bridge that translates a business concept ("Visa Consultation") into a Calendly concept ("this specific event type UUID belonging to this doctor's account").

---

## 3. Booking Flow — End to End

### 3.1 Step-by-Step Backend Flow

```
[1] User navigates to /services (packages page)
    Frontend renders a static service catalog — no API call.
    Service names, durations, and prices are hardcoded in the frontend.
    NEXT_PUBLIC_SERVICE_KEY_* env vars provide the stable keys for each service.

[2] User selects "Visa Consultation"
    Frontend reads process.env.NEXT_PUBLIC_SERVICE_KEY_VISA_CONSULTATION = "visa_consultation"
    GET /api/v1/services/{service_key}/doctors
    ← List of doctors offering this service (from doctor_services JOIN doctors)

[3] User selects Dr. Priya
    GET /api/v1/doctors/{doctor_id}/availability?service_id={id}&date_from=...&date_to=...
    Backend:
      1. Fetch doctor_services row → get calendly_event_type_uri + doctor.calendly_pat
      2. Call Calendly: GET /event_type_available_times?event_type={uri}&start={}&end={}
         Authorization: Bearer {doctor.calendly_pat}
      3. Filter out slots already booked or reserved:
           SELECT slot_time FROM bookings
           WHERE doctor_service_id = DS1
             AND status NOT IN ('cancelled')
             AND slot_time BETWEEN $start AND $end
           UNION
           SELECT slot_time FROM slot_reservations
           WHERE doctor_service_id = DS1
             AND expires_at > now()
             AND slot_time BETWEEN $start AND $end
             AND user_id != $current_user  ← user's own reservation is still shown
      4. Subtract booked/reserved slots from Calendly response
    ← Slot list with greyed_out flag per slot

[4] User selects a slot (e.g. 10:00 AM May 15)
    Frontend greys out slot optimistically (local state, not persisted)

[5] POST /api/v1/bookings/reserve
    Body: { doctor_service_id: "DS1", slot_time: "2026-05-15T10:00:00Z" }
    Backend:
      1. Auth check → 401
      2. Load doctor_services row, confirm is_active → 404
      3. Confirm no confirmed booking exists for this slot (hard check)
      4. Conditional upsert into slot_reservations (atomic, see §1.4)
         → 409 if RETURNING is empty (slot taken)
      5. DELETE old slot_reservation for this user on DS1 if they're switching slots
    ← { reservation_id: "SR1", slot_time: "...", expires_at: "T+5min" }

    Frontend:
      - Starts 5-minute countdown
      - Slot is now greyed out for other users (next availability poll will exclude it)
      - If countdown hits 0 → POST /bookings/reserve/expire (cleanup) + show "Slot released"

[6] User clicks "Proceed to Payment"
    POST /api/v1/payments/create-order
    Body: { doctor_service_id: "DS1", slot_time: "2026-05-15T10:00:00Z" }
    Backend:
      1. Auth check → 401
      2. Verify slot_reservation exists for this user + DS1 + slot_time, not expired → 409
      3. Resolve effective price: COALESCE(ds.price_override, s.base_amount)
      4. INSERT bookings (status='pending_payment', slot_expires_at=now()+15min)
      5. INSERT payments (status='pending')
      6. POST Razorpay /v1/orders { amount, currency, receipt=P1.id,
                                     close_by=slot_expires_at as Unix ts }
      7. UPDATE payments SET razorpay_order_id='order_ABC'
      8. DELETE slot_reservations WHERE id=SR1  ← hand off to booking-level lock
    ← { order_id: "order_ABC", amount, currency, booking_id: "B1", key: "rzp_live_..." }

    Frontend:
      - Replaces 5-min timer with 15-min timer
      - Opens Razorpay SDK modal

[7] User completes payment in Razorpay modal
    Razorpay handler fires with { razorpay_payment_id, razorpay_order_id, razorpay_signature }
    POST /api/v1/payments/verify
    Backend:
      1. HMAC-SHA256: HMAC(secret, "order_ABC|pay_XYZ") == signature → 400 if mismatch
      2. Atomic slot confirm:
           UPDATE bookings
             SET status='confirmed', payment_id='P1', updated_at=now()
           WHERE id='B1'
             AND status='pending_payment'
             AND slot_expires_at > now()
           RETURNING id
         → empty RETURNING = slot expired → trigger refund → 409
      3. UPDATE payments SET status='succeeded', razorpay_payment_id, razorpay_signature
      4. Trigger Calendly event creation (async background task)
    ← { ok: true, booking_id: "B1" }

[8] Calendly Event Creation (background, after step 7)
    Backend:
      1. Load doctor_services → get calendly_event_type_uri + doctor.calendly_pat
      2. POST https://api.calendly.com/one_off_event_types (or scheduled_events)
         Authorization: Bearer {doctor.calendly_pat}
         Body: { event_type_uri, start_time, invitee: { name, email } }
      3. UPDATE bookings SET
           scheduled_at=..., calendly_event_uri=..., calendly_invitee_uri=...
         WHERE id='B1'
    Calendly sends confirmation email to user automatically.

[9] User sees "Booking Confirmed" screen
    Shows: slot time, doctor name, service name, Calendly invitee link for reschedule/cancel
```

---

### 3.2 DB State Transitions

| Step | Table | Operation | Key columns |
|---|---|---|---|
| Reserve slot (step 5) | `slot_reservations` | UPSERT | `user_id`, `expires_at=+5min` |
| Create order (step 6) | `bookings` | INSERT | `status='pending_payment'`, `slot_expires_at=+15min` |
| Create order (step 6) | `payments` | INSERT | `status='pending'` |
| Create order (step 6) | `payments` | UPDATE | `razorpay_order_id='order_ABC'` |
| Create order (step 6) | `slot_reservations` | DELETE | hand off done |
| Verify payment (step 7) | `bookings` | UPDATE | `status='confirmed'`, `payment_id` |
| Verify payment (step 7) | `payments` | UPDATE | `status='succeeded'`, `razorpay_payment_id`, `razorpay_signature` |
| Calendly created (step 8) | `bookings` | UPDATE | `scheduled_at`, `calendly_event_uri`, `calendly_invitee_uri` |
| Payment failed | `payments` | UPDATE | `status='failed'`, `metadata.error` |
| Payment failed | `bookings` | UPDATE | `status='cancelled'` |
| Slot reservation expired | `slot_reservations` | DELETE (cleanup) | — |
| Booking slot expired (step 7 atomic fail) | `payments` | UPDATE | `status='refunded'` |
| Manual cancel | `bookings` | UPDATE | `status='cancelled'` |

---

## 4. Race Condition & Concurrency Strategy

### 4.1 Layer 1 — Slot Reservation (5-minute soft lock)

The conditional upsert in `slot_reservations` (§1.4) is the first barrier.

```
User A: tries to reserve DS1/10:00 → INSERT succeeds → RETURNING = SR1
User B: tries to reserve DS1/10:00 at the same millisecond
         → INSERT conflicts on UNIQUE(DS1, 10:00)
         → DO UPDATE fires: WHERE slot_reservations.expires_at <= now() → FALSE (just inserted)
         → RETURNING empty → User B gets 409 "Slot already reserved"
```

No application-level locking needed. PostgreSQL's UNIQUE constraint serialises concurrent inserts atomically.

### 4.2 Layer 2 — Booking Confirmation (15-minute hard lock)

When the user pays, the atomic UPDATE in `POST /payments/verify` is the definitive lock:

```sql
UPDATE bookings
  SET status='confirmed', payment_id=$p_id, updated_at=now()
WHERE id = $booking_id
  AND status = 'pending_payment'      -- not already claimed
  AND slot_expires_at > now()         -- not expired
RETURNING id;
```

Two concurrent verify requests for the same booking:
- First request: `status='pending_payment'` matches → UPDATE succeeds → returns row.
- Second request: `status='confirmed'` now → WHERE clause fails → RETURNING empty → 409.

### 4.3 Layer 3 — External Calendly Bookings

A doctor may book a slot directly in Calendly outside of DentNav. This creates an **external booking** that DentNav doesn't know about.

**Prevention:** Before creating the Calendly event (step 8), re-fetch availability:

```python
async def verify_slot_still_available(ds: DoctorService, slot_time: datetime) -> bool:
    # Re-call Calendly availability API for a narrow window
    slots = await calendly.get_available_times(
        event_type_uri=ds.calendly_event_type_uri,
        pat=doctor.calendly_pat,
        start_time=slot_time - timedelta(minutes=1),
        end_time=slot_time + timedelta(minutes=1),
    )
    return any(s.start_time == slot_time for s in slots)
```

If the slot is gone (doctor booked it externally):
1. Mark `bookings.status = 'cancelled'`
2. Initiate full Razorpay refund
3. Notify user: "Your slot was no longer available. Full refund initiated."

**Detection via Calendly Webhooks:** Subscribe to `invitee.created` events. If an external booking comes in for a slot that has a `pending_payment` booking in our DB, immediately cancel that booking and start a refund before the user pays. Store raw events in `calendly_webhook_events` for idempotent replay.

### 4.4 Layer 4 — Razorpay `close_by`

The Razorpay order is created with `close_by = unix(slot_expires_at)`. Razorpay blocks payments after that timestamp at the gateway level — no money moves, no refund needed. Backend slot check in `/verify` is a belt-and-suspenders defence for the extremely rare case where Razorpay processes past `close_by`.

### 4.5 Idempotency

| Endpoint | Idempotency strategy |
|---|---|
| `POST /bookings/reserve` | Conditional upsert — safe to retry |
| `POST /payments/create-order` | Check for existing `pending` payment for same user+DS+slot first |
| `POST /payments/verify` | `WHERE status='pending_payment'` guard — second call is a no-op |
| `POST /payments/webhook/razorpay` | Check `payments.status != 'succeeded'` before writing |
| Calendly webhook | `UNIQUE(calendly_uuid)` on `calendly_webhook_events` — duplicate events are ignored |

---

## 5. API Contracts

### 5.1 `GET /api/v1/services`

Returns all active services. No auth required.

```jsonc
// Response 200
[
  {
    "id": "uuid",
    "service_key": "visa_consultation",
    "name": "Visa Consultation",
    "description": "...",
    "duration_minutes": 60,
    "base_amount": 0,       // 0 = TBD
    "currency": "usd",
    "is_consultation": true  // duration_minutes IS NOT NULL
  },
  ...
]
```

---

### 5.2 `GET /api/v1/services/{service_id}/doctors`

Returns doctors who offer this service.

```jsonc
// Response 200
[
  {
    "doctor_id": "uuid",
    "name": "Dr. Priya Sharma",
    "bio": "...",
    "photo_url": "...",
    "specializations": ["visa", "residency"],
    "effective_amount": 5000,  // COALESCE(ds.price_override, s.base_amount)
    "currency": "inr"
  }
]
```

---

### 5.3 `GET /api/v1/doctors/{doctor_id}/availability`

Proxies Calendly availability for a doctor's event type. Auth required.

```
Query params:
  service_id  required  — resolves to doctor_services row → calendly_event_type_uri
  date_from   required  — ISO 8601 date
  date_to     required  — ISO 8601 date (max 7 days ahead)

Response 200:
[
  {
    "slot_time": "2026-05-15T10:00:00Z",
    "status": "available"     // "available" | "reserved" | "booked"
  },
  {
    "slot_time": "2026-05-15T11:00:00Z",
    "status": "reserved"      // another user has a 5-min hold
  }
]
```

Backend logic:
1. `SELECT calendly_event_type_uri, doctor.calendly_pat FROM doctor_services JOIN doctors`
2. Call Calendly `/event_type_available_times`
3. Query `slot_reservations` and `bookings` for this `doctor_service_id` in the date range
4. Annotate each Calendly slot with its status

---

### 5.4 `POST /api/v1/bookings/reserve`

Creates a 5-minute soft lock on a slot.

```jsonc
// Request
{
  "doctor_service_id": "uuid",
  "slot_time": "2026-05-15T10:00:00Z"
}

// Response 200
{
  "reservation_id": "uuid",
  "slot_time": "2026-05-15T10:00:00Z",
  "expires_at": "2026-05-15T09:15:00Z"
}

// Response 409
{ "error": "slot_taken", "message": "This slot has just been reserved by another user." }
```

---

### 5.5 `POST /api/v1/bookings/reserve/release`

Releases a slot reservation before the 5 minutes are up (user navigates back).

```jsonc
// Request
{ "reservation_id": "uuid" }

// Response 200
{ "ok": true }
```

---

### 5.6 `POST /api/v1/payments/create-order`

Promotes a slot reservation into a 15-minute booking hold and creates the Razorpay order.

```jsonc
// Request
{
  "doctor_service_id": "uuid",
  "slot_time": "2026-05-15T10:00:00Z"
}

// Response 200
{
  "order_id": "order_ABC",
  "amount": 5000,
  "currency": "inr",
  "booking_id": "uuid",
  "expires_at": "2026-05-15T09:30:00Z",   // slot_expires_at
  "razorpay_key": "rzp_live_..."
}

// Response 409
{ "error": "reservation_expired", "message": "Your slot reservation expired. Please select a new slot." }
```

---

### 5.7 `POST /api/v1/payments/verify`

HMAC verification + atomic booking confirmation.

```jsonc
// Request
{
  "razorpay_payment_id": "pay_XYZ",
  "razorpay_order_id":   "order_ABC",
  "razorpay_signature":  "sig_..."
}

// Response 200
{
  "ok": true,
  "booking_id": "uuid",
  "slot_time": "2026-05-15T10:00:00Z",
  "doctor_name": "Dr. Priya Sharma",
  "calendly_invitee_uri": "https://calendly.com/cancellations/..."
}

// Response 400
{ "error": "signature_mismatch" }

// Response 409
{
  "error": "slot_expired",
  "message": "Your slot expired before payment was confirmed. A full refund has been initiated."
}
```

---

### 5.8 `POST /api/v1/payments/webhook/razorpay`

Server-to-server backup. Verified via `X-Razorpay-Signature` against `RAZORPAY_WEBHOOK_SECRET`.

```
Events handled:
  payment.captured  → run same logic as /verify if payment not already succeeded
  payment.failed    → mark payment failed, cancel booking if still pending_payment
  refund.processed  → mark payment refunded
```

---

### 5.9 `POST /api/v1/webhooks/calendly`

Receives Calendly events for external booking detection and sync.

```
Events handled:
  invitee.created   → cross-check against pending bookings for same slot
                      if conflict → cancel booking, refund payment
  invitee.canceled  → if we created this event, update bookings.status='cancelled'
                      optionally auto-rebook or notify user

Idempotency: INSERT INTO calendly_webhook_events ON CONFLICT DO NOTHING
```

---

## 6. Calendly Sync Strategy

### 6.1 What needs syncing

Each `doctor_services` row contains a `calendly_event_type_uuid`. This must match an actual, active event type in that doctor's Calendly account. If the doctor deletes or renames their event type, the mapping breaks.

### 6.2 Sync triggers

| Trigger | When | Action |
|---|---|---|
| **Doctor onboarding** | Admin adds a doctor | Call `GET /event_types?user={uri}` with doctor's PAT → seed `doctor_services` rows |
| **On-demand via admin API** | Admin clicks "Sync" | Same as above — idempotent upsert |
| **Periodic (weekly)** | Background job | Refresh `calendly_event_type_uri` + detect deleted types |
| **Calendly webhook** | `event_type.*` events (if available) | Update or soft-delete affected `doctor_services` |

### 6.3 Sync algorithm

```python
async def sync_doctor_calendly(doctor: Doctor) -> None:
    event_types = await calendly.list_event_types(
        user_uri=doctor.calendly_user_uri,
        pat=doctor.calendly_pat,
    )
    active_uuids = {et.uuid for et in event_types if et.active}

    # Soft-disable doctor_services rows whose event type is gone
    await db.execute(
        """
        UPDATE doctor_services
          SET is_active = false
        WHERE doctor_id = $1
          AND calendly_event_type_uuid NOT IN $2
          AND is_active = true
        """,
        doctor.id, active_uuids
    )

    # Upsert known event types (admin must map UUID → service_id separately)
    for et in event_types:
        await db.execute(
            """
            INSERT INTO doctor_services (id, doctor_id, calendly_event_type_uuid,
                                         calendly_event_type_uri, is_active)
            VALUES (gen_random_uuid(), $1, $2, $3, $4)
            ON CONFLICT (doctor_id, calendly_event_type_uuid) DO UPDATE
              SET calendly_event_type_uri = EXCLUDED.calendly_event_type_uri,
                  is_active = EXCLUDED.is_active
            """,
            doctor.id, et.uuid, et.uri, et.active
        )
```

### 6.4 Deletion strategy

| Object | Strategy | Reason |
|---|---|---|
| `doctors` | Soft-delete (`is_active=false`) | Hard FK from `doctor_services` |
| `doctor_services` | Soft-delete (`is_active=false`) | Hard FK from `bookings` |
| `services` | Soft-delete (`is_active=false`) | Historical payment records |
| `slot_reservations` | Hard delete when expired | Ephemeral data, no historical value |

---

## 7. Failure Scenarios & Recovery

| Scenario | Detection | Recovery |
|---|---|---|
| User reserves slot, closes browser | `expires_at <= now()` | Slot auto-visible in next availability poll; cleanup via periodic DELETE |
| Payment succeeds but browser tab closes before `/verify` | Razorpay `payment.captured` webhook fires | Webhook runs same verify logic; Calendly event created from webhook |
| Calendly API is down at event creation time | Exception caught after payment confirmed | Booking is `confirmed` but `calendly_event_uri=NULL`; retry queue picks it up |
| Doctor deletes Calendly event type | Weekly sync detects missing UUID | `doctor_services.is_active=false`; existing bookings unaffected |
| External booking takes a slot between reservation and payment | `/verify` step: re-check Calendly availability | Cancel booking, refund via Razorpay, notify user |
| Razorpay webhook arrives twice | `payment.status = 'succeeded'` check | Skip — idempotent guard |
| `slot_reservations` row not deleted after booking created | Periodic cleanup | `DELETE WHERE expires_at <= now()` |
| Network error during Razorpay order creation | Exception in `create-order` | No payment row committed → user can retry |

---

## 8. Environment Variables

```bash
# Razorpay
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...

# Calendly (no global token — each doctor has their own PAT stored in DB)
CALENDLY_WEBHOOK_SIGNING_KEY=...   # For verifying Calendly webhook payloads

# Frontend (public — safe to expose)
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_live_...

# Service keys — must match service_key values in the services table
# Frontend uses these to pass a stable key to the booking API; no UUIDs hardcoded.
NEXT_PUBLIC_SERVICE_KEY_ANALYSIS_ACCESS=analysis_access
NEXT_PUBLIC_SERVICE_KEY_INTRO_CONSULTATION=intro_consultation
NEXT_PUBLIC_SERVICE_KEY_VISA_CONSULTATION=visa_consultation
NEXT_PUBLIC_SERVICE_KEY_INTERVIEW_PREPARATION=interview_preparation
NEXT_PUBLIC_SERVICE_KEY_CV_SOP_REVIEW=cv_sop_review
NEXT_PUBLIC_SERVICE_KEY_CAAPID_ASSISTANCE=caapid_assistance
NEXT_PUBLIC_SERVICE_KEY_LICENSE_GUIDANCE=license_guidance
```

> Doctor Calendly PATs live in `doctors.calendly_pat`, encrypted at rest.
> No global Calendly token. No per-doctor env vars.

---

## 9. Migration Plan

```
0005 — create services table + seed rows (service_key not yet present)
0006 — create doctors table
0007 — create doctor_services table
0008 — create slot_reservations table
0009 — create bookings table (uses doctor_service_id; payment_id FK deferred)
0010 — create payments table + deferred bookings.payment_id FK
0011 — add service_key column to services + seed values  ← live
0012 — create calendly_webhook_events table (optional)
```

---

## 10. Architectural Decisions Summary

| Decision | Alternative considered | Why this wins |
|---|---|---|
| `service_key` (not `slug`) | Keep `slug` | `slug` implies URL segment; `service_key` clearly signals machine-readable lookup key used by backend logic and frontend env vars |
| Remove `category` | Keep as enum | Derivable from `duration_minutes IS NULL`; two fields for one boolean concept is redundant |
| PostgreSQL conditional upsert for slot locks | Redis TTL key, advisory locks | One fewer infrastructure dependency; UNIQUE constraint handles race atomically; `expires_at` replaces TTL transparently; no lock daemon |
| `doctor_services` junction table | Embed event_type_uuid directly on doctors | One doctor can offer many services each with a different event type; services are business concepts independent of who delivers them; pricing overrides per doctor |
| Store `calendly_event_type_uri` (not just UUID) | Reconstruct URI from UUID | Calendly API accepts full URIs; avoids string construction in hot paths |
| Soft delete everywhere | Hard delete | FK integrity; historical payment/booking records remain valid; can re-activate |
| Per-doctor PAT in `doctors` table (encrypted) | Env vars per doctor, OAuth per doctor | Env vars don't scale to N doctors; OAuth is out of scope; encrypted column is the pragmatic middle ground |
| `close_by` on Razorpay order | Application-level expiry check only | Gateway-level enforcement — no money moves after expiry, nothing to refund; belt-and-suspenders on top |
| Calendly as availability source of truth | Mirror availability in our DB | Calendly handles buffer times, external blocks, calendar overlaps — mirroring introduces sync lag and is fragile |
