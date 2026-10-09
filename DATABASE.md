# EcoLoop — Database Schema

**Database:** PostgreSQL (primary) + Redis (caching / OTP TTL)
**Conventions:**
- All IDs are UUIDs v4.
- All timestamps are UTC ISO 8601.
- Soft deletes via `deleted_at` where noted.

---

## Entity Relationship Overview

```
users ──────────────< pickups >──────────────── collectors
  |                      |
  |                      └──── classifications
  └── eco_point_transactions
  └── wallet (1:1)

recyclers (= collectors acting as recyclers)
  └── recycler_slots
```

---

## Tables

### `users`

| Column          | Type         | Constraints              | Description                    |
|-----------------|--------------|--------------------------|--------------------------------|
| `user_id`       | UUID         | PK, default gen_random_uuid() | Unique user identifier    |
| `name`          | VARCHAR(255) | NOT NULL                 | Full name                      |
| `email`         | VARCHAR(255) | UNIQUE, NOT NULL         | Login email                    |
| `phone`         | VARCHAR(20)  | UNIQUE                   | Mobile number for OTP          |
| `password_hash` | TEXT         | NOT NULL                 | bcrypt hash                    |
| `role`          | ENUM         | NOT NULL, default `user` | `user`, `collector`, `admin`   |
| `eco_points`    | INTEGER      | NOT NULL, default 0      | Current EcoPoints balance      |
| `created_at`    | TIMESTAMPTZ  | default NOW()            | Account creation time          |
| `updated_at`    | TIMESTAMPTZ  | default NOW()            | Last update time               |
| `deleted_at`    | TIMESTAMPTZ  | nullable                 | Soft delete timestamp          |

---

### `collectors`

| Column               | Type         | Constraints       | Description                          |
|----------------------|--------------|-------------------|--------------------------------------|
| `collector_id`       | UUID         | PK                | Unique collector identifier          |
| `user_id`            | UUID         | FK → users        | Linked user account                  |
| `business_name`      | VARCHAR(255) | NOT NULL          | Registered business name             |
| `license_number`     | VARCHAR(100) | UNIQUE            | Certification / license ID           |
| `address`            | TEXT         | NOT NULL          | Operational address                  |
| `lat`                | DECIMAL(9,6) | NOT NULL          | Latitude                             |
| `lng`                | DECIMAL(9,6) | NOT NULL          | Longitude                            |
| `rating`             | DECIMAL(2,1) | default 0.0       | Average rating (0.0–5.0)             |
| `accepted_categories`| TEXT[]       | NOT NULL          | Array of accepted e-waste categories |
| `is_active`          | BOOLEAN      | default true      | Whether collector is accepting jobs  |
| `created_at`         | TIMESTAMPTZ  | default NOW()     |                                      |

---

### `classifications`

| Column               | Type         | Constraints       | Description                                  |
|----------------------|--------------|-------------------|----------------------------------------------|
| `classification_id`  | UUID         | PK                | Unique classification record                 |
| `user_id`            | UUID         | FK → users        | User who submitted the image(s)              |
| `category`           | VARCHAR(100) | NOT NULL          | Normalized e-waste category                  |
| `confidence_score`   | DECIMAL(4,3) | NOT NULL          | AI confidence (0.000–1.000)                  |
| `safety_tips`        | TEXT[]       | NOT NULL          | Array of safety recommendation strings       |
| `estimated_weight_kg`| DECIMAL(5,2) | nullable          | AI-estimated item weight                     |
| `raw_label`          | VARCHAR(255) | NOT NULL          | Raw label from AI model                      |
| `image_urls`         | TEXT[]       | NOT NULL          | S3/Cloudinary URLs of uploaded images        |
| `user_confirmed`     | BOOLEAN      | default false     | Did user confirm or correct the AI result?   |
| `created_at`         | TIMESTAMPTZ  | default NOW()     |                                              |

---

### `pickups`

| Column               | Type         | Constraints               | Description                              |
|----------------------|--------------|---------------------------|------------------------------------------|
| `pickup_id`          | UUID         | PK                        | Unique pickup request ID                 |
| `user_id`            | UUID         | FK → users, NOT NULL      | User requesting pickup                   |
| `collector_id`       | UUID         | FK → collectors, nullable | Assigned collector (set on acceptance)   |
| `classification_id`  | UUID         | FK → classifications      | Associated AI classification             |
| `item_description`   | TEXT         | NOT NULL                  | User-provided description                |
| `scheduled_at`       | TIMESTAMPTZ  | NOT NULL                  | Requested pickup date/time               |
| `address_street`     | VARCHAR(255) | NOT NULL                  | Pickup street address                    |
| `address_city`       | VARCHAR(100) | NOT NULL                  | City                                     |
| `address_state`      | VARCHAR(100) | NOT NULL                  | State / province                         |
| `address_pincode`    | VARCHAR(20)  | NOT NULL                  | Postal / PIN code                        |
| `address_lat`        | DECIMAL(9,6) | NOT NULL                  | Latitude of pickup location              |
| `address_lng`        | DECIMAL(9,6) | NOT NULL                  | Longitude of pickup location             |
| `otp`                | CHAR(6)      | NOT NULL                  | 6-digit OTP for handoff verification     |
| `otp_expires_at`     | TIMESTAMPTZ  | NOT NULL                  | OTP expiry (30 minutes from creation)    |
| `status`             | ENUM         | NOT NULL, default `pending` | See Pickup Statuses below             |
| `cancellation_reason`| TEXT         | nullable                  | Reason if cancelled                      |
| `created_at`         | TIMESTAMPTZ  | default NOW()             |                                          |
| `updated_at`         | TIMESTAMPTZ  | default NOW()             |                                          |

**Pickup Status ENUM:** `pending`, `accepted`, `in_transit`, `completed`, `cancelled`

---

### `eco_point_transactions`

| Column           | Type         | Constraints          | Description                             |
|------------------|--------------|----------------------|-----------------------------------------|
| `transaction_id` | UUID         | PK                   | Unique transaction ID                   |
| `user_id`        | UUID         | FK → users, NOT NULL | Recipient user                          |
| `pickup_id`      | UUID         | FK → pickups         | Associated pickup (nullable for bonuses)|
| `points`         | INTEGER      | NOT NULL             | Points awarded (positive) or spent (negative) |
| `reason`         | VARCHAR(255) | NOT NULL             | e.g., `"pickup_completed"`, `"referral_bonus"` |
| `created_at`     | TIMESTAMPTZ  | default NOW()        |                                         |

---

### `recycler_slots`

| Column        | Type        | Constraints              | Description                         |
|---------------|-------------|--------------------------|-------------------------------------|
| `slot_id`     | UUID        | PK                       | Unique slot ID                      |
| `collector_id`| UUID        | FK → collectors, NOT NULL| Owning collector                    |
| `starts_at`   | TIMESTAMPTZ | NOT NULL                 | Slot start datetime                 |
| `ends_at`     | TIMESTAMPTZ | NOT NULL                 | Slot end datetime                   |
| `is_booked`   | BOOLEAN     | default false            | Whether slot is already taken       |
| `pickup_id`   | UUID        | FK → pickups, nullable   | Booking reference                   |

---

## Redis Usage

| Key Pattern                     | TTL       | Purpose                         |
|---------------------------------|-----------|---------------------------------|
| `otp:{pickup_id}`               | 30 min    | OTP value for active pickup     |
| `session:{user_id}`             | 24 hours  | JWT session invalidation list   |
| `recyclers:nearby:{lat}:{lng}`  | 5 min     | Cached nearby recycler results  |

---

## Indexes

```sql
CREATE INDEX idx_pickups_user_id       ON pickups(user_id);
CREATE INDEX idx_pickups_collector_id  ON pickups(collector_id);
CREATE INDEX idx_pickups_status        ON pickups(status);
CREATE INDEX idx_pickups_scheduled_at  ON pickups(scheduled_at);
CREATE INDEX idx_collectors_location   ON collectors USING GIST(ll_to_earth(lat, lng));
CREATE INDEX idx_classifications_user  ON classifications(user_id);
```

---

## Notes

- CO₂ savings are calculated at query time from `estimated_weight_kg` × category-specific emission factor; not stored directly.
- OTP is generated fresh on pickup creation; re-generation on request resets `otp_expires_at`.
- EcoPoints balance on `users.eco_points` is the denormalized running total; `eco_point_transactions` is the audit log.
