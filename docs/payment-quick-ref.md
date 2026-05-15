# DentNav — Payment Quick Reference

---

## Page 1 — Schemas

### Live Tables

**`users`**

| Column | Type |
|---|---|
| `user_id` | VARCHAR(36) PK |
| `email` | VARCHAR(320) UNIQUE NOT NULL |
| `first_name` | VARCHAR(120) NOT NULL |
| `last_name` | VARCHAR(120) NOT NULL |
| `has_filled_questionnaire` | BOOLEAN NOT NULL |
| `created_at` / `updated_at` | TIMESTAMPTZ NOT NULL |

**`analyses`**

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `user_id` | FK → users (NULL until claimed) |
| `performance` | INTEGER NOT NULL — readiness score 0–100 |
| `answers` | JSONB NOT NULL |
| `llm_result` | JSONB NOT NULL — server-only until payment succeeded |
| `created_at` / `updated_at` | TIMESTAMPTZ NOT NULL |

> No `paid` column. Access to `llm_result` is gated by checking `payments` for a `succeeded` row with `reference_id = analyses.id`.

---

### Planned Tables (migrations 0005 – 0011)

**`services`**

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `service_key` | VARCHAR(100) UNIQUE NOT NULL — machine key (e.g. `visa_consultation`) |
| `name` | VARCHAR(255) NOT NULL — display label |
| `description` | TEXT DEFAULT `''` |
| `duration_minutes` | INTEGER — NULL = analysis, NOT NULL = consultation |
| `base_amount` | INTEGER NOT NULL — cents, 0 = TBD |
| `currency` | VARCHAR(10) DEFAULT `'usd'` |
| `is_active` | BOOLEAN DEFAULT `true` |

No `category` or `calendly_event_type_uuid`. `duration_minutes IS NULL` identifies analysis services.

---

**`doctors`**

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `name` | VARCHAR(255) NOT NULL |
| `bio` / `photo_url` | TEXT |
| `specializations` | TEXT[] |
| `calendly_user_uri` | VARCHAR(512) — cached from PAT lookup |
| `calendly_pat` | TEXT — **encrypted at rest, never returned by API** |
| `is_active` | BOOLEAN DEFAULT `true` |

---

**`doctor_services`**

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `doctor_id` | FK → doctors CASCADE |
| `service_id` | FK → services RESTRICT |
| `calendly_event_type_uuid` | VARCHAR(255) NOT NULL |
| `calendly_event_type_uri` | TEXT NOT NULL |
| `price_override` | INTEGER — NULL → use `services.base_amount` |
| `is_active` | BOOLEAN DEFAULT `true` |

`UNIQUE (doctor_id, service_id)` — one event type per doctor per service.
Effective price: `COALESCE(price_override, base_amount)`

---

**`slot_reservations`** — 5-min soft lock (no Redis)

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `doctor_service_id` | FK → doctor_services CASCADE |
| `slot_time` | TIMESTAMPTZ NOT NULL |
| `user_id` | FK → users CASCADE |
| `expires_at` | TIMESTAMPTZ NOT NULL — `now() + 5 min` |

`UNIQUE (doctor_service_id, slot_time)` — the atomicity guarantee.

---

**`bookings`**

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `user_id` | FK → users RESTRICT |
| `doctor_service_id` | FK → doctor_services RESTRICT |
| `payment_id` | FK → payments — NULL until paid |
| `status` | `pending_payment` · `confirmed` · `completed` · `cancelled` · `no_show` |
| `slot_time` | TIMESTAMPTZ |
| `slot_expires_at` | TIMESTAMPTZ — 15-min payment hold |
| `scheduled_at` | TIMESTAMPTZ — set by Calendly |
| `calendly_event_uri` | TEXT |
| `calendly_invitee_uri` | TEXT |

---

**`payments`**

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `user_id` | FK → users NOT NULL |
| `doctor_service_id` | FK → doctor_services — NULL for analysis access |
| `reference_id` | `analyses.id` or `bookings.id` |
| `razorpay_order_id` | VARCHAR(255) UNIQUE NOT NULL |
| `razorpay_payment_id` | VARCHAR(255) UNIQUE |
| `razorpay_signature` | VARCHAR(512) |
| `amount` | INTEGER NOT NULL — snapshot |
| `currency` | VARCHAR(10) DEFAULT `'usd'` |
| `status` | `pending` · `succeeded` · `failed` · `expired` · `refunded` |
| `metadata` | JSONB DEFAULT `'{}'` |

---
---

## Page 2 — Consultation Booking Flow

### Actors
Frontend · Backend · PostgreSQL · Razorpay · Calendly

---

### Happy Path

```
1. Frontend renders static service catalog (no API call)
   NEXT_PUBLIC_SERVICE_KEY_* env vars hold stable keys per service.
   When user picks a service the frontend reads the matching env var
   (e.g. NEXT_PUBLIC_SERVICE_KEY_VISA_CONSULTATION = "visa_consultation").

2. User picks service → GET /api/v1/services/{service_key}/doctors
   ← doctors offering it, with effective_amount

3. User picks doctor → GET /api/v1/doctors/{id}/availability?service_id=...
   Backend: fetches Calendly slots via doctor's PAT + doctor_services event type URI
            subtracts booked + reserved slots from result
   ← [{ slot_time, status: available|reserved|booked }]

4. User picks slot (frontend greys out optimistically)
   POST /api/v1/bookings/reserve { doctor_service_id, slot_time }
   Backend: conditional upsert into slot_reservations
            UNIQUE(doctor_service_id, slot_time) enforces atomicity
            → 409 if another user holds an active reservation
   ← { reservation_id, expires_at: +5min }
   Frontend: starts 5-min countdown

5. User clicks Pay
   POST /api/v1/payments/create-order { doctor_service_id, slot_time }
   Backend:
     Verify slot_reservation still valid for this user
     INSERT bookings (status='pending_payment', slot_expires_at=now()+15min)
     INSERT payments (status='pending', amount/currency snapshot)
     POST razorpay /v1/orders { amount, currency, close_by=unix(slot_expires_at) }
     UPDATE payments SET razorpay_order_id='order_ABC'
     DELETE slot_reservations WHERE id=SR1   ← booking is now the lock
   ← { order_id, amount, currency, booking_id, expires_at, razorpay_key }
   Frontend: replaces 5-min timer with 15-min timer, opens Razorpay modal

6. User pays in Razorpay popup
   Razorpay handler → { razorpay_payment_id, razorpay_order_id, razorpay_signature }

7. POST /api/v1/payments/verify { payment_id, order_id, signature }
   Backend:
     HMAC_SHA256(key_secret, "order_ABC|pay_XYZ") == signature  →  else 400

     -- Atomic slot confirm (eliminates TOCTOU)
     UPDATE bookings
       SET status='confirmed', payment_id='P1'
       WHERE id='B1' AND status='pending_payment' AND slot_expires_at > now()
     RETURNING id
     → empty: expired → refund immediately → 409

     UPDATE payments SET status='succeeded', razorpay_payment_id, razorpay_signature

8. Backend (background) → Calendly
   Re-verify slot still available (external booking guard)
   POST calendly /scheduled_events { event_type_uri, start_time, invitee }
     Authorization: Bearer {doctor.calendly_pat}
   UPDATE bookings SET scheduled_at, calendly_event_uri, calendly_invitee_uri
   Calendly sends confirmation email automatically.
```

---

### Failure Cases

| Case | Trigger | Outcome |
|---|---|---|
| **A** — card declined | Razorpay `payment.failed` | `payments='failed'` · `bookings='cancelled'` · redirect to services |
| **B** — slot expired (timer) | Frontend countdown hits 0 | `bookings='cancelled'` · `payments='expired'` · redirect to calendar |
| **C** — sig mismatch | HMAC check fails | 400 · rows stay pending · cleanup expires them |
| **D** — paid after expiry | `close_by` passed | Razorpay rejects at gateway (no money moves). If it slips through: verify detects expired → immediate refund → 409 |
| **E** — external Calendly booking | Slot gone at step 8 | Cancel booking · refund payment · notify user |

---

### Slot Locking (PostgreSQL, no Redis)

```sql
-- Reserve: atomic, race-safe
INSERT INTO slot_reservations (doctor_service_id, slot_time, user_id, expires_at)
VALUES ($ds, $time, $user, now() + interval '5 minutes')
ON CONFLICT (doctor_service_id, slot_time) DO UPDATE
  SET user_id = EXCLUDED.user_id, expires_at = EXCLUDED.expires_at
  WHERE slot_reservations.expires_at <= now()   -- only overwrite expired
RETURNING id;
-- empty RETURNING = slot taken → 409

-- Confirm: atomic, TOCTOU-safe
UPDATE bookings
  SET status='confirmed', payment_id=$pid, updated_at=now()
WHERE id=$bid AND status='pending_payment' AND slot_expires_at > now()
RETURNING id;
-- empty RETURNING = expired → refund
```

---

### Razorpay Webhook (backup)

```
POST /api/v1/payments/webhook/razorpay
  Verify X-Razorpay-Signature against RAZORPAY_WEBHOOK_SECRET

payment.captured → skip if already succeeded (idempotent) → run same verify logic
payment.failed   → mark failed, cancel booking if still pending_payment
refund.processed → mark refunded
```

---

### Analysis Access (no calendar)

```
POST /payments/create-order { reference_id: "A1" }
  doctor_service_id = NULL, reference_id = analyses.id

POST /payments/verify (same HMAC flow, no slot check)
  UPDATE payments SET status='succeeded'

GET /analysis/{A1}/full
  SELECT EXISTS(payments WHERE reference_id='A1' AND status='succeeded'
                           AND doctor_service_id IS NULL)
  → 402 if false, else return analyses.llm_result
```

---

### Env Vars

```bash
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
CALENDLY_WEBHOOK_SIGNING_KEY=...
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_live_...

# Service keys — match service_key values in DB; frontend uses these instead of hardcoding UUIDs
NEXT_PUBLIC_SERVICE_KEY_ANALYSIS_ACCESS=analysis_access
NEXT_PUBLIC_SERVICE_KEY_INTRO_CONSULTATION=intro_consultation
NEXT_PUBLIC_SERVICE_KEY_VISA_CONSULTATION=visa_consultation
NEXT_PUBLIC_SERVICE_KEY_INTERVIEW_PREPARATION=interview_preparation
NEXT_PUBLIC_SERVICE_KEY_CV_SOP_REVIEW=cv_sop_review
NEXT_PUBLIC_SERVICE_KEY_CAAPID_ASSISTANCE=caapid_assistance
NEXT_PUBLIC_SERVICE_KEY_LICENSE_GUIDANCE=license_guidance
```

No global `CALENDLY_API_TOKEN` — each doctor's PAT lives in `doctors.calendly_pat` (encrypted).
