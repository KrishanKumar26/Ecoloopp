# EcoLoop — Product Requirements Document (PRD)

**Version:** 1.0
**Date:** October 2026
**Status:** Draft — Hackathon MVP

---

## 1. Problem Statement

Electronic waste (e-waste) is one of the fastest-growing waste streams globally. Most households and small businesses have no easy, trusted way to dispose of old electronics responsibly. Existing recycling options are fragmented, inconvenient, and offer no incentive for participation.

---

## 2. Vision

EcoLoop closes the gap between waste generators and certified recyclers through a seamless mobile-first experience: snap a photo, get an instant AI assessment, schedule a free pickup, and earn rewards for doing the right thing.

---

## 3. Target Users

| Persona         | Description                                              |
|-----------------|----------------------------------------------------------|
| **User**        | Household or business with e-waste to dispose of         |
| **Collector**   | Certified recycler or pickup agent                       |
| **Admin**       | Platform operator managing users, collectors, and data   |

---

## 4. Core MVP Flow

1. **Image Upload** — User photographs their e-waste item(s).
2. **AI E-Waste Identification** — Classification model identifies device type, brand (if visible), and estimated age.
3. **Safety Recommendation** — Tailored handling tips (e.g., "Do not puncture lithium batteries").
4. **Recycler Selection** — User browses or is auto-matched to nearby certified recyclers.
5. **Pickup Scheduling** — User selects a date/time slot; a pickup request is created with status `pending`.
6. **Collector Acceptance** — Collector reviews and accepts the request; status moves to `accepted`.
7. **OTP Verification** — At handoff, collector enters the OTP sent to the user; status moves to `completed`.
8. **Award 75 EcoPoints** — System credits 75 EcoPoints to the user's wallet upon successful OTP verification.
9. **Environmental Impact Dashboard** — User sees lifetime CO₂ saved, items recycled, and leaderboard rank.

---

## 5. Functional Requirements

### 5.1 Authentication
- Email/phone registration with OTP-based login.
- JWT-based session management.
- Role-based access: `user`, `collector`, `admin`.

### 5.2 E-Waste Submission
- Upload single or multiple images (JPEG/PNG, max 10 MB each).
- AI returns: `category`, `confidence_score`, `safety_tips[]`, `estimated_weight_kg`.
- User can confirm or correct the AI classification.

### 5.3 Recycler Discovery
- Display recyclers within configurable radius (default 25 km).
- Show name, rating, accepted_categories[], distance, and available slots.
- User selects preferred recycler before scheduling.

### 5.4 Pickup Scheduling
- Pickup statuses: `pending` → `accepted` → `in_transit` → `completed` | `cancelled`.
- Each pickup stores: `user_id`, `collector_id`, `item_description`, `scheduled_at`, `address`, `otp`, `status`.
- OTP is 6-digit numeric, valid for 30 minutes.

### 5.5 EcoPoints
- 75 EcoPoints awarded per completed pickup.
- Bonus multipliers (future): bulk pickups, referrals.
- Points visible in user wallet; redeemable for vouchers (post-MVP).

### 5.6 Impact Dashboard
- Per-user: total items recycled, estimated CO₂ saved (kg), EcoPoints balance.
- Global: aggregate statistics and top-10 leaderboard.

---

## 6. Non-Functional Requirements

| Category       | Requirement                                      |
|----------------|--------------------------------------------------|
| Performance    | API response < 500 ms (p95, excluding AI calls)  |
| AI Latency     | Classification result < 3 s                      |
| Availability   | 99.5% uptime target                              |
| Security       | HTTPS everywhere, hashed passwords, OTP expiry   |
| Scalability    | Stateless API, horizontal scaling ready          |
| Accessibility  | WCAG 2.1 AA for web surfaces                     |

---

## 7. Out of Scope (MVP)

- Payment processing or recycler payouts.
- In-app chat between users and collectors.
- Multi-language support.
- Native push notifications (email/SMS only for MVP).
- EcoPoints redemption marketplace.

---

## 8. Success Metrics

| Metric                        | Target (Hackathon Demo)       |
|-------------------------------|-------------------------------|
| Pickups created               | ≥ 10 demo pickups             |
| AI classification accuracy    | ≥ 80% on test set             |
| End-to-end flow time          | < 5 minutes from upload to OTP|
| EcoPoints awarded             | Automatically on OTP verify   |

---

## 9. Timeline (Hackathon)

| Phase          | Deliverable                            |
|----------------|----------------------------------------|
| Day 1          | Project scaffold + DB schema + API spec|
| Day 2          | Backend APIs + AI service integration  |
| Day 3          | Frontend screens + end-to-end flow     |
| Day 4          | Testing, polish, demo prep             |
