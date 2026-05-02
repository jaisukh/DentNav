# DentNav — Payment Quick Reference

---

## Page 1 — Schemas

### Existing

**`users`**

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `email` | VARCHAR(320) UNIQUE NOT NULL |
| `first_name` | VARCHAR(120) NOT NULL |
| `last_name` | VARCHAR(120) NOT NULL |
| `has_filled` | BOOLEAN NOT NULL |
| `created_at` | TIMESTAMPTZ NOT NULL |
| `updated_at` | TIMESTAMPTZ NOT NULL |

**`analyses`**

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `user_id` | FK → users (NULL until OAuth claim) |
| `paid` | BOOLEAN NOT NULL — access gate for full payload |
| `country` | VARCHAR(120) NOT NULL |
| `degree` | VARCHAR(120) NOT NULL |
| `years_of_exp` | VARCHAR(120) NOT NULL |
| `performance` | INTEGER NOT NULL (0–100) |
| `answers` | JSONB NOT NULL |
| `payload` | JSONB NOT NULL — server-only until `paid=true` |
| `created_at` | TIMESTAMPTZ NOT NULL |
| `updated_at` | TIMESTAMPTZ NOT NULL |

---

### New (migrations 0004 – 0006)

**`services`** — migration 0004

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `slug` | VARCHAR(100) UNIQUE NOT NULL |
| `name` | VARCHAR(255) NOT NULL |
| `description` | TEXT DEFAULT `''` |
| `category` | `'analysis'` \| `'consultation'` |
| `duration_minutes` | INTEGER (NULL for analysis) |
| `amount` | INTEGER NOT NULL — minor unit (cents) |
| `currency` | VARCHAR(10) DEFAULT `'usd'` |
| `calendly_event_type_uuid` | VARCHAR(255) (NULL for analysis) |
| `is_active` | BOOLEAN DEFAULT `true` |

Seed rows: `analysis_access` · `consultation_introductory` · `consultation_visa` · `consultation_interview` · `consultation_cv_sop` · `consultation_caapid` · `consultation_license`

---

**`payments`** — migration 0005

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `user_id` | FK → users NOT NULL |
| `service_id` | FK → services NOT NULL |
| `reference_id` | `analyses.id` or `bookings.id` |
| `razorpay_order_id` | VARCHAR(255) UNIQUE NOT NULL |
| `razorpay_payment_id` | VARCHAR(255) UNIQUE |
| `razorpay_signature` | VARCHAR(512) |
| `amount` | INTEGER NOT NULL (snapshot at purchase time) |
| `currency` | VARCHAR(10) DEFAULT `'usd'` |
| `status` | `pending` · `succeeded` · `failed` · `expired` · `refunded` |
| `metadata` | JSONB DEFAULT `'{}'` |

---

**`bookings`** — migration 0006 (consultations only)

| Column | Type |
|---|---|
| `id` | VARCHAR(36) PK |
| `user_id` | FK → users NOT NULL |
| `service_id` | FK → services NOT NULL |
| `payment_id` | FK → payments (NULL until paid) |
| `status` | `pending_payment` · `confirmed` · `completed` · `cancelled` · `no_show` |
| `slot_time` | TIMESTAMPTZ |
| `slot_expires_at` | TIMESTAMPTZ (`slot_time + 15 min`) |
| `scheduled_at` | TIMESTAMPTZ (set by Calendly) |
| `calendly_event_id` | VARCHAR(255) |
| `calendly_invitee_url` | TEXT |
| `notes` | TEXT |

---
---

## Page 2 — Consultation Payment Flow

### Actors
Frontend · Backend · Redis · Razorpay · PostgreSQL · Calendly

---

### Happy Path

```
1. User opens /landing/services
   GET /api/v1/services  →  service cards rendered

2. User clicks service  →  calendar opens
   GET /api/v1/bookings/available-slots?service_id=S1
     Backend: reads services.calendly_event_type_uuid → proxies Calendly

3. User selects slot
   Backend: SET slot:{time} = U1  EX 900  (Redis soft-lock, 15 min)
   WebSocket broadcast → slot greyed out on all other clients

4. User clicks Pay Now
   POST /api/v1/payments/create-order  { service_id, slot_time }
     INSERT bookings  (status='pending_payment', slot_expires_at=now()+15min)
     INSERT payments  (status='pending', amount/currency snapshot from services)
     POST razorpay.com/v1/orders  { amount, currency, close_by=slot_expires_at }
     UPDATE payments SET razorpay_order_id='order_ABC'
   ← { order_id, amount, currency, key }

5. Frontend opens Razorpay popup
   User pays  →  Razorpay returns { payment_id, order_id, signature }

6. POST /api/v1/payments/verify  { payment_id, order_id, signature }
   Backend:
     HMAC_SHA256(key_secret, "order_ABC|pay_XYZ") == signature  →  else 400

     -- Atomic check + flip (eliminates TOCTOU race)
     UPDATE bookings
       SET status='confirmed', payment_id=P1
       WHERE id='B1'
         AND status='pending_payment'
         AND slot_expires_at > now()
     RETURNING id
     → empty result: slot expired between check and write → refund + 409 (Case D)

     UPDATE payments  status='succeeded', razorpay_payment_id, razorpay_signature

7. Backend → Calendly
   POST calendly.com/scheduled_events  { event_type_uuid, start_time, invitee }
   UPDATE bookings  SET scheduled_at, calendly_event_id, calendly_invitee_url
   Calendly sends confirmation email automatically.
```

---

### Failure Cases

| Case | Trigger | Outcome |
|---|---|---|
| **A** — card declined | Razorpay `payment.failed` callback | UPDATE payments `failed` · UPDATE bookings `cancelled` · redirect to services |
| **B** — slot expired (frontend) | Countdown hits 0 | POST /bookings/{id}/expire · Redis key deleted · slot unlocked on all clients |
| **C** — sig mismatch | HMAC check fails | 400 · rows stay pending · cleanup job expires them |
| **D** — paid after expiry | `close_by` passed on Razorpay order | Razorpay rejects at gateway (no money moves). If payment slips through: verify detects expired slot → immediate refund → 409 |

---

### Webhook (backup)

```
POST /api/v1/payments/webhook/razorpay
  Verify X-Razorpay-Signature
  Idempotent: skip if payment.status already 'succeeded' or 'refunded'
  Run same slot check as verify (Case D)
  Run same DB writes + Calendly creation if not already done
```

---

### Analysis Access (no calendar)

Identical to steps 4 – 6 above, with:
- No booking row / no slot locking
- `reference_id` = `analyses.id`
- On verify success: `UPDATE analyses SET paid=true`

---

### Env Vars

```bash
RAZORPAY_KEY_ID=rzp_live_…
RAZORPAY_KEY_SECRET=…
RAZORPAY_WEBHOOK_SECRET=…
CALENDLY_API_TOKEN=…
CALENDLY_WEBHOOK_SECRET=…
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_live_…
```
