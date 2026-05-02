# DentNav — Payment Integration & Consultation Booking

> **Scope:** Database schemas (existing + planned) and the end-to-end Razorpay
> payment flow for consultation bookings. Questionnaire-access payment follows
> a simpler variant of the same flow (no calendar step).

---

## Page 1 — Database Schemas

---

### 1.1 Existing Tables

#### `users`

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `email` | VARCHAR(320) UNIQUE NOT NULL | Google account email |
| `first_name` | VARCHAR(120) NOT NULL | Default `''` |
| `last_name` | VARCHAR(120) NOT NULL | Default `''` |
| `has_filled` | BOOLEAN NOT NULL | `true` after questionnaire submitted |
| `created_at` | TIMESTAMPTZ NOT NULL | `server_default=now()` |
| `updated_at` | TIMESTAMPTZ NOT NULL | Auto-updated on write |

#### `analyses`

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `user_id` | VARCHAR(36) FK → users `SET NULL` | NULL until OAuth claim |
| `paid` | BOOLEAN NOT NULL | `false` → **access gate** for full payload |
| `country` | VARCHAR(120) NOT NULL | Extracted from LLM payload |
| `degree` | VARCHAR(120) NOT NULL | Extracted from LLM payload |
| `years_of_exp` | VARCHAR(120) NOT NULL | Extracted from LLM payload |
| `performance` | INTEGER NOT NULL | Readiness score 0–100 |
| `answers` | JSONB NOT NULL | Raw questionnaire answers |
| `payload` | JSONB NOT NULL | Full LLM response — server-only until `paid=true` |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

Index: `ix_analyses_user_id` on `(user_id)`

---

### 1.2 New Tables (migrations 0004 + 0005 + 0006)

#### `services` — migration 0004

Single source of truth for every purchasable product. Seeded once; updated
in-place when prices or Calendly event types change — no code deploy needed.

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `slug` | VARCHAR(100) UNIQUE NOT NULL | Machine key: `analysis_access`, `consultation_visa`, … |
| `name` | VARCHAR(255) NOT NULL | Display name: `"Visa Consultation"` |
| `description` | TEXT NOT NULL DEFAULT `''` | Shown on the services page |
| `category` | VARCHAR(50) NOT NULL | `analysis` \| `consultation` |
| `duration_minutes` | INTEGER | NULL for `analysis` category |
| `amount` | INTEGER NOT NULL | Price in the currency's minor unit (e.g. cents for USD) — never a float |
| `currency` | VARCHAR(10) NOT NULL DEFAULT `'usd'` | |
| `calendly_event_type_uuid` | VARCHAR(255) | NULL for `analysis` category |
| `is_active` | BOOLEAN NOT NULL DEFAULT `true` | Soft-disable — hides from UI without deleting |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

**Why each column exists:**

| Column | Why it's necessary |
|---|---|
| `id` | Stable FK target for `payments.service_id` and `bookings.service_id`. Using a UUID rather than `slug` means renaming a service doesn't break existing payment rows. |
| `slug` | Machine-readable key used in code and API calls (`"consultation_visa"`). Keeps logic readable without hardcoding UUIDs everywhere. |
| `name` | Human-readable label rendered directly in the UI (service card title, Razorpay popup description, email confirmations). Lives here so it can be edited without a code deploy. |
| `description` | Longer copy shown on the services page beneath the title. Same reason — content editable via DB, not code. |
| `category` | Determines the booking flow. `analysis` → no calendar, links to `analyses` table. `consultation` → calendar + slot locking + Calendly event. Backend uses this to pick the right handler at `POST /payments/create-order`. |
| `duration_minutes` | Passed to Calendly when creating the scheduled event. NULL for `analysis` since there's no session to schedule. Stored here so changing a session length doesn't require a code change. |
| `amount` | Current price in the currency's minor unit. Copied (snapshotted) into `payments.amount` at order creation so the payment record always reflects what the user was actually charged, even if the price changes later. |
| `currency` | Paired with `amount`. Determines which Razorpay currency code is sent in the order payload. Defaults to `usd`. |
| `calendly_event_type_uuid` | The UUID of the Calendly Event Type for this consultation (e.g. the "Visa Consultation - 60 min" event). Backend reads this when proxying the available-slots call and when creating the Calendly event post-payment. NULL for `analysis`. Stored here so switching Calendly event types needs only a DB update. |
| `is_active` | Lets you disable a service (hide from UI, reject new bookings) without deleting its row — deletion would break FK references in historical `payments` and `bookings` rows. |
| `created_at` / `updated_at` | Audit trail — useful for knowing when a price was last changed. |

**Seed data (migration 0004):**

| `slug` | `name` | `category` | `duration_minutes` | `amount` |
|---|---|---|---|---|
| `analysis_access` | Analysis Access | `analysis` | NULL | TBD |
| `consultation_introductory` | Introductory Consultation | `consultation` | 45 | TBD |
| `consultation_visa` | Visa Consultation | `consultation` | 60 | TBD |
| `consultation_interview` | Interview Preparation | `consultation` | 60 | TBD |
| `consultation_cv_sop` | CV / SOP Review | `consultation` | 60 | TBD |
| `consultation_caapid` | CAAPID Assistance | `consultation` | 60 | TBD |
| `consultation_license` | License Guidance | `consultation` | 60 | TBD |

---

#### `payments` — migration 0005

Tracks every payment attempt, one row per checkout initiated.

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `user_id` | VARCHAR(36) FK → users NOT NULL | User must be signed in to pay |
| `service_id` | VARCHAR(36) FK → services NOT NULL | Which service was purchased |
| `reference_id` | VARCHAR(36) | `analyses.id` for `analysis` · `bookings.id` for `consultation` |
| `razorpay_order_id` | VARCHAR(255) UNIQUE NOT NULL | `order_ABC` — set at order creation |
| `razorpay_payment_id` | VARCHAR(255) UNIQUE | `pay_XYZ` — set after frontend verification |
| `razorpay_signature` | VARCHAR(512) | HMAC-SHA256 signature stored for audit |
| `amount` | INTEGER NOT NULL | Snapshot of price at time of payment — never a float |
| `currency` | VARCHAR(10) NOT NULL DEFAULT `'usd'` | Snapshot from `services.currency` |
| `status` | VARCHAR(50) NOT NULL DEFAULT `'pending'` | `pending \| succeeded \| failed \| expired \| refunded` |
| `metadata` | JSONB NOT NULL DEFAULT `'{}'` | Extra context (error codes, refund reason, etc.) |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

> `amount` and `currency` are copied from `services` at order creation time
> so the payment record reflects what the user was actually charged, even if
> the service price changes later.

```sql
-- Prevents a second successful charge for the same analysis at the DB level
CREATE UNIQUE INDEX uq_payments_analysis_succeeded
  ON payments (reference_id)
  WHERE service_id = (SELECT id FROM services WHERE slug = 'analysis_access')
    AND status = 'succeeded';
```

#### `bookings` — migration 0006 (consultation services only)

One row per consultation booking, created before payment is taken.

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) PK | UUID v4 |
| `user_id` | VARCHAR(36) FK → users NOT NULL | |
| `service_id` | VARCHAR(36) FK → services NOT NULL | Determines duration + Calendly event type |
| `payment_id` | VARCHAR(36) FK → payments | NULL until payment succeeds |
| `status` | VARCHAR(50) NOT NULL DEFAULT `'pending_payment'` | `pending_payment \| confirmed \| completed \| cancelled \| no_show` |
| `slot_time` | TIMESTAMPTZ | Calendar slot chosen by user — set before payment |
| `slot_expires_at` | TIMESTAMPTZ | `slot_time + 15 min` — slot hold TTL |
| `scheduled_at` | TIMESTAMPTZ | Set by Calendly after event confirmed |
| `calendly_event_id` | VARCHAR(255) | Calendly event UUID |
| `calendly_invitee_url` | TEXT | Calendly invitee link for cancellations |
| `notes` | TEXT | Internal prep notes |
| `created_at` | TIMESTAMPTZ NOT NULL | |
| `updated_at` | TIMESTAMPTZ NOT NULL | |

> `duration_minutes` and `calendly_event_type_uuid` are read from `services`
> at booking time — not stored on `bookings` directly.

---

### 1.3 ID Relationship Map

```
services (S1: slug='consultation_visa')
  └── bookings (B1)          ← service_id = S1
        └── payments (P1)    ← service_id = S1, reference_id = B1
              └── razorpay_order_id = order_ABC
                    └── razorpay_payment_id = pay_XYZ
                          └── razorpay_signature (verification proof)

users (U1)
  └── analyses (A1)          ← user_id = U1
  └── bookings (B1)          ← user_id = U1
  └── payments (P1)          ← user_id = U1
```

---

### 1.5 Status Transitions

**`payments.status`**
```
pending → succeeded   (signature verified on backend)
        → failed      (Razorpay failure callback → POST /payments/fail)
        → expired     (slot lock expired before payment completed)
        → refunded    (manual/webhook refund)
```

**`bookings.status`**
```
pending_payment → confirmed   (payment succeeded + Calendly event created)
               → cancelled    (payment failed / slot expired)
confirmed      → completed    (session done)
confirmed      → cancelled    (user/admin cancels)
confirmed      → no_show      (user missed session)
```

---
---

## Page 2 — Razorpay Payment Flow (Consultation Booking)

> This flow covers all services **except** the questionnaire analysis unlock.
> The analysis-access flow is identical except it skips the calendar step
> (steps 1–3) and links `reference_id` to `analyses.id` instead of
> `bookings.id`.

---

### Actors

| Actor | Description |
|---|---|
| **Frontend** | Next.js App Router (user's browser) |
| **Backend** | FastAPI service |
| **Razorpay** | Payment gateway (order creation, checkout SDK, webhooks) |
| **Database** | PostgreSQL — `users`, `services`, `bookings`, `payments` |
| **Calendly** | Calendar scheduling (slot availability + event creation) |

---

### 2.1 User Lands on Services Page

```
User navigates to /landing/services
  (protected: middleware.ts + AuthGuard must pass)

Services displayed (non-questionnaire):
  • Introductory Consultation (45 min)
  • Visa Consultation (60 min)
  • Interview Preparation (60 min)
  • CV / SOP Review (60 min)
  • CAAPID Assistance (60 min)
  • License Guidance (60 min)

User clicks a service card → e.g. "Book Visa Consultation"
  Frontend captures: { service_id: "S1" }   ← loaded from GET /api/v1/services
```

---

### 2.2 Calendar UI — Slot Selection

```
Frontend renders calendar UI
  GET /api/v1/bookings/available-slots?service_id=S1
    Backend: SELECT calendly_event_type_uuid FROM services WHERE id='S1'
    Proxies → Calendly API for open slots on that event type
  ← [ { slot_time: "2026-05-10T10:00:00Z" }, … ]

User picks a slot → e.g. 10:00 AM on May 10
  Frontend holds selection in local state (not yet persisted)
  User clicks "Proceed to Payment"
```

---

### 2.3 Slot Lock — Reserve Booking Row

```
POST /api/v1/bookings/reserve
  Cookie: dentnav_user_id={id}
  Body: {
    service_id: "S1",
    slot_time:  "2026-05-10T10:00:00Z"
  }

Backend:
  1. Verify session cookie → 401 if missing
  2. SELECT * FROM services WHERE id='S1' AND is_active=true AND category='consultation'
     → 404 if not found or inactive
  3. Check slot is still available (race guard — SELECT FOR UPDATE) → 409 if taken
  4. INSERT bookings (
       id              = B1 (new UUID),
       user_id         = U1,
       service_id      = S1,
       status          = 'pending_payment',
       slot_time       = '2026-05-10T10:00:00',
       slot_expires_at = now() + 15 min       ← slot hold TTL
     )

← { booking_id: "B1", slot_time: "…", expires_at: "…" }

Frontend:
  Starts 15-minute countdown timer
  If timer reaches 0 before payment → POST /bookings/{B1}/expire
  → UPDATE bookings SET status='cancelled' WHERE id='B1'
  → redirect user back to calendar to pick again
```

---

### 2.4 Create Payment Row + Razorpay Order

```
POST /api/v1/payments/create-order
  Cookie: dentnav_user_id={id}
  Body: { booking_id: "B1" }

Backend:
  1. Verify session cookie → 401
  2. Load booking B1, confirm owner = U1, status = 'pending_payment' → 403/404
  3. Confirm slot not yet expired (slot_expires_at > now()) → 410 if expired
  4. SELECT amount, currency FROM services WHERE id = B1.service_id

  5. INSERT payments (
       id           = P1 (new UUID),
       user_id      = U1,
       service_id   = S1,
       reference_id = B1,
       status       = 'pending',
       amount = services.amount,   ← snapshot at time of purchase
       currency     = services.currency
     )

  5. POST https://api.razorpay.com/v1/orders
       Authorization: Basic (RAZORPAY_KEY_ID:RAZORPAY_KEY_SECRET)
       Body: {
         amount:   5000,
         currency: "usd",
         receipt:  "P1",
         close_by: 1746866400,   ← Unix timestamp of slot_expires_at
                                    Razorpay rejects payment after this point
                                    at the gateway level — nothing to refund
         notes: {
           payment_id:  "P1",
           booking_id:  "B1",
           user_id:     "U1"
         }
       }

  Razorpay responds:
  {
    id:       "order_ABC",
    amount:   5000,
    currency: "usd",
    status:   "created",
    receipt:  "P1"
  }

  6. UPDATE payments SET razorpay_order_id = 'order_ABC' WHERE id = 'P1'

← {
    order_id:   "order_ABC",
    amount:     5000,
    currency:   "usd",
    key:        "rzp_live_…",
    booking_id: "B1",
    user_name:  "Harsha Arra",
    user_email: "user@example.com"
  }
```

---

### 2.5 Frontend — Razorpay Checkout SDK

```javascript
// Frontend opens the Razorpay payment modal
const rzp = new Razorpay({
  key:        "rzp_live_…",
  order_id:   "order_ABC",
  amount:     5000,
  currency:   "usd",
  name:       "DentNav",
  description: "Visa Consultation — 60 min",
  prefill: {
    name:  "Harsha Arra",
    email: "user@example.com"
  },
  handler: function (response) {
    // SUCCESS — send all three IDs to backend for verification
    verifyPayment(response)
  },
  modal: {
    ondismiss: function () {
      // User closed the modal without paying — no action needed
      // Slot hold timer is still running
    }
  }
})
rzp.open()
```

> Razorpay shows an embedded popup — no page redirect. The user enters
> card / UPI / net banking details inside the modal.
> Razorpay internally creates `pay_XYZ` and returns it in the `handler` callback.

---

### 2.6 SUCCESS PATH — Backend Signature Verification

```
Frontend receives from Razorpay handler:
{
  razorpay_payment_id: "pay_XYZ",
  razorpay_order_id:   "order_ABC",
  razorpay_signature:  "sig_abc123…"
}

POST /api/v1/payments/verify
  Cookie: dentnav_user_id={id}
  Body: {
    payment_id: "pay_XYZ",
    order_id:   "order_ABC",
    signature:  "sig_abc123…"
  }

Backend verification (CRITICAL — never trust frontend alone):
  Step 1 — HMAC signature check
    generated = HMAC_SHA256(
      key     = RAZORPAY_KEY_SECRET,
      message = "order_ABC|pay_XYZ"
    )
    if generated != signature → 400 "Signature mismatch"

  Step 2 — Atomic slot check + confirm (eliminates TOCTOU race)
    A separate SELECT + UPDATE would leave a window where the slot expires
    between the check and the write. Instead, the check and the flip are
    a single statement:

    UPDATE bookings
      SET status     = 'confirmed',
          payment_id = 'P1',
          updated_at = now()
      WHERE id = 'B1'
        AND status = 'pending_payment'
        AND slot_expires_at > now()
    RETURNING id

    → RETURNING is empty: slot expired (or already confirmed by another request)
      → treat as Case D: issue refund + return 409

DB write on success (RETURNING returned a row):
  UPDATE payments
    SET status               = 'succeeded',
        razorpay_payment_id  = 'pay_XYZ',
        razorpay_signature   = 'sig_abc123…',
        updated_at           = now()
  WHERE razorpay_order_id = 'order_ABC'

← { ok: true, booking_id: "B1" }
```

---

### 2.7 Calendly Event Creation

```
Triggered immediately after bookings.status = 'confirmed'

Backend → Calendly API
  SELECT calendly_event_type_uuid FROM services WHERE id = B1.service_id
  POST https://api.calendly.com/scheduled_events
    Authorization: Bearer CALENDLY_API_TOKEN
    Body: {
      event_type_uuid: services.calendly_event_type_uuid,
      start_time:      "2026-05-10T10:00:00Z",
      invitee: {
        name:  "Harsha Arra",
        email: "user@example.com"
      }
    }

Calendly responds:
  {
    resource: {
      uri:         "https://api.calendly.com/scheduled_events/EVT_123",
      start_time:  "2026-05-10T10:00:00Z"
    }
  }

DB write:
  UPDATE bookings
    SET scheduled_at          = '2026-05-10T10:00:00Z',
        calendly_event_id     = 'EVT_123',
        calendly_invitee_url  = 'https://calendly.com/cancellations/…',
        updated_at            = now()
  WHERE id = 'B1'

Calendly sends confirmation email to user automatically.
```

---

### 2.8 FAILURE PATH

**Case A — Payment failed inside Razorpay modal**

```javascript
// Razorpay fires this on card decline, timeout, etc.
rzp.on('payment.failed', function (response) {
  notifyBackend(response.error)
})
```

```
POST /api/v1/payments/fail
  Body: { order_id: "order_ABC", error_code: "BAD_REQUEST_ERROR", ... }

Backend:
  UPDATE payments
    SET status     = 'failed',
        metadata   = { error: response.error },
        updated_at = now()
  WHERE razorpay_order_id = 'order_ABC'

  UPDATE bookings
    SET status     = 'cancelled',
        updated_at = now()
  WHERE id = 'B1'

← { ok: true }
Frontend → redirect user back to /landing/services with error toast
```

**Case B — Slot expired before payment (frontend-driven)**

```
Frontend countdown timer hits 0:
  POST /api/v1/bookings/{B1}/expire

Backend:
  UPDATE bookings SET status='cancelled' WHERE id='B1' AND status='pending_payment'
  UPDATE payments SET status='expired'  WHERE reference_id='B1' AND status='pending'

Frontend → redirect to calendar with "Slot expired — please pick another time"
```

> The Razorpay order (`order_ABC`) is still alive — Razorpay orders have
> **no automatic expiry**. If the user somehow completes payment after this
> point, Case D handles it.

**Case C — Signature mismatch**

```
Backend returns 400.
Frontend shows generic error.
Booking remains 'pending_payment', payment remains 'pending'.
A background job (or next POST /expire call) cleans up stale rows.
```

**Case D — User pays after slot has already expired (late payment)**

> With `close_by` set on the Razorpay order, Razorpay blocks the payment at
> the gateway level the moment `close_by` passes — no money moves, nothing to
> refund. This eliminates the dangerous window entirely.
>
> The backend slot check in `POST /verify` is kept as a secondary defence for
> any edge case where `close_by` enforcement is delayed on Razorpay's side.

```
Timeline:
  T+0:00  User reserves slot B1 → slot_expires_at = T+0:15
  T+0:14  User opens Razorpay modal
            order_ABC has close_by = T+0:15
  T+0:15  Frontend timer fires → POST /bookings/{B1}/expire
            bookings.status → 'cancelled'
            payments.status → 'expired'
          Razorpay order also closes (close_by passed)
  T+0:17  User tries to complete payment inside the modal
            Razorpay rejects at gateway — "order closed"
            payment.failed callback fires with error code ORDER_CLOSED

  No money moves. No refund needed.
```

**Secondary defence — backend slot check (belt-and-suspenders):**

```
If Razorpay somehow processes a payment past close_by (rare, treat as a bug):

POST /api/v1/payments/verify
  Step 1 — Signature check → valid
  Step 2 — Slot check:
    SELECT status, slot_expires_at FROM bookings WHERE id='B1'
    status = 'cancelled'  OR  slot_expires_at < now()
    → LATE PAYMENT DETECTED

  Immediate refund:
    POST https://api.razorpay.com/v1/payments/pay_XYZ/refund
      Body: { amount: 5000 }

  UPDATE payments SET status='refunded', metadata={ refund_reason:'slot_expired' }

← 409 { error: "slot_expired", message: "Your slot expired. A full refund has been initiated." }
```

---

### 2.9 Razorpay Webhook (Backup Confirmation)

Razorpay also sends server-to-server webhooks. These act as a safety net if
the frontend tab was closed after payment but before `POST /payments/verify`.

```
POST /api/v1/payments/webhook/razorpay
  X-Razorpay-Signature: verified against RAZORPAY_WEBHOOK_SECRET

Event: payment.captured
Payload:
{
  event: "payment.captured",
  payload: {
    payment: {
      entity: {
        id:       "pay_XYZ",
        order_id: "order_ABC",
        status:   "captured"
      }
    }
  }
}

Backend:
  1. Verify X-Razorpay-Signature → reject if invalid
  2. Look up payment by razorpay_order_id = 'order_ABC'
  3. Idempotency: skip if payment.status already 'succeeded' or 'refunded'
  4. Slot expiry check (same as §2.6 Step 2) → refund immediately if expired (Case D)
  5. Run same DB writes as §2.6 (verify path)
  6. Run Calendly event creation if not already done (calendly_event_id IS NULL)
```

> **Primary truth:** Signature verification (§2.6) is the primary confirmation
> path. The webhook is a backup for dropped frontend connections.
> Unlike Stripe (where the webhook IS the primary), Razorpay makes the
> frontend callback the happy path — but you must verify the signature
> on the backend before trusting it.

---

### 2.10 Complete State Transition Table

| User action | Table | Operation | Key columns set |
|---|---|---|---|
| Click "Book" → pick slot | — | — | (frontend only) |
| POST /bookings/reserve | `bookings` | INSERT | `status='pending_payment'`, `slot_time`, `slot_expires_at` |
| POST /payments/create-order | `payments` | INSERT | `status='pending'`, `reference_id=B1` |
| POST /payments/create-order | `payments` | UPDATE | `razorpay_order_id='order_ABC'` |
| Razorpay checkout success | — | — | Frontend receives `pay_XYZ`, `signature` |
| POST /payments/verify | `payments` | UPDATE | `status='succeeded'`, `razorpay_payment_id`, `razorpay_signature` |
| POST /payments/verify | `bookings` | UPDATE | `status='confirmed'`, `payment_id=P1` |
| Calendly event created | `bookings` | UPDATE | `scheduled_at`, `calendly_event_id`, `calendly_invitee_url` |
| Session completed | `bookings` | UPDATE | `status='completed'` |
| Payment failed | `payments` | UPDATE | `status='failed'`, `metadata.error` |
| Payment failed | `bookings` | UPDATE | `status='cancelled'` |
| Slot expired (frontend timer) | `bookings` | UPDATE | `status='cancelled'` |
| Slot expired (frontend timer) | `payments` | UPDATE | `status='expired'` |
| Late payment detected (Case D) | `payments` | UPDATE | `status='refunded'`, `metadata.refund_reason='slot_expired'` |
| Webhook backup | `payments` | UPDATE | same as verify (idempotent + slot check) |
| Manual refund | `payments` | UPDATE | `status='refunded'` |
| Manual refund | `bookings` | UPDATE | `status='cancelled'` |

---

### 2.11 API Endpoints (Consultation Payment)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/services` | No | List all `is_active=true` services |
| GET | `/api/v1/bookings/available-slots` | Cookie | Proxy to Calendly — `?service_id=` |
| POST | `/api/v1/bookings/reserve` | Cookie | Lock slot → INSERT bookings row |
| POST | `/api/v1/bookings/{id}/expire` | Cookie | Release expired slot |
| POST | `/api/v1/payments/create-order` | Cookie | INSERT payment + create Razorpay order |
| POST | `/api/v1/payments/verify` | Cookie | HMAC verify → confirm booking |
| POST | `/api/v1/payments/fail` | Cookie | Record failure → cancel booking |
| POST | `/api/v1/payments/webhook/razorpay` | Razorpay-Sig | Backup server-to-server confirmation |

---

### 2.12 Environment Variables

Prices, durations, and Calendly event type UUIDs live in the `services` table
(seeded in migration 0004) — not in env vars. Only secrets and gateway
credentials belong here.

```bash
# Razorpay
RAZORPAY_KEY_ID=rzp_live_…
RAZORPAY_KEY_SECRET=…
RAZORPAY_WEBHOOK_SECRET=…

# Calendly
CALENDLY_API_TOKEN=…
CALENDLY_WEBHOOK_SECRET=…   # For verifying Calendly webhooks

# Frontend (public — safe to expose)
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_live_…
```

> To change a price or add a service, run an UPDATE / INSERT on the `services`
> table directly — no code change or redeploy required.

---

