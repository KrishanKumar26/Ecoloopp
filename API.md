# EcoLoop — API Reference

**Base URL:** `https://api.ecoloop.app/v1`
**Auth:** Bearer JWT in `Authorization` header
**Content-Type:** `application/json` (multipart/form-data for uploads)

---

## Pickup Statuses (Canonical)

| Status       | Description                                              |
|--------------|----------------------------------------------------------|
| `pending`    | Pickup created by user, awaiting collector acceptance    |
| `accepted`   | Collector has accepted the pickup request                |
| `in_transit` | Collector is on the way                                  |
| `completed`  | OTP verified; pickup confirmed and EcoPoints awarded     |
| `cancelled`  | Cancelled by user or collector                           |

---

## Authentication

### POST /auth/register
Register a new user or collector.

**Request Body:**
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "password": "string",
  "role": "user | collector"
}
```

**Response `201`:**
```json
{
  "user_id": "uuid",
  "name": "string",
  "email": "string",
  "role": "user | collector",
  "token": "jwt_string"
}
```

---

### POST /auth/login
**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response `200`:**
```json
{
  "token": "jwt_string",
  "user_id": "uuid",
  "role": "user | collector"
}
```

---

## AI Classification

### POST /ai/classify
Upload one or more images for e-waste classification.

**Request:** `multipart/form-data`
| Field    | Type   | Description               |
|----------|--------|---------------------------|
| `images` | file[] | JPEG/PNG, max 10 MB each  |

**Response `200`:**
```json
{
  "classification_id": "uuid",
  "category": "string",
  "confidence_score": 0.95,
  "safety_tips": ["string"],
  "estimated_weight_kg": 1.2,
  "raw_label": "string"
}
```

**Field Definitions:**
- `category` — normalized e-waste category (e.g., `"Mobile Phone"`, `"Laptop"`, `"CRT Monitor"`)
- `confidence_score` — float 0–1; scores below 0.6 trigger a manual review prompt
- `safety_tips` — array of plain-language handling instructions
- `estimated_weight_kg` — AI-estimated weight; used for CO₂ impact calculation
- `raw_label` — the model's original label before normalization

---

## Recyclers

### GET /recyclers
Fetch nearby certified recyclers.

**Query Parameters:**
| Param       | Type    | Default | Description                  |
|-------------|---------|---------|------------------------------|
| `lat`       | float   | —       | User latitude (required)     |
| `lng`       | float   | —       | User longitude (required)    |
| `radius_km` | integer | `25`    | Search radius in km          |
| `category`  | string  | —       | Filter by accepted category  |

**Response `200`:**
```json
{
  "recyclers": [
    {
      "recycler_id": "uuid",
      "name": "string",
      "address": "string",
      "lat": 0.0,
      "lng": 0.0,
      "distance_km": 3.4,
      "rating": 4.7,
      "accepted_categories": ["string"],
      "available_slots": ["2026-10-10T09:00:00Z"]
    }
  ]
}
```

---

## Pickups

### POST /pickups
Create a new pickup request.

**Request Body:**
```json
{
  "user_id": "uuid",
  "collector_id": "uuid",
  "classification_id": "uuid",
  "item_description": "string",
  "scheduled_at": "ISO8601 datetime",
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "pincode": "string",
    "lat": 0.0,
    "lng": 0.0
  }
}
```

**Response `201`:**
```json
{
  "pickup_id": "uuid",
  "user_id": "uuid",
  "collector_id": "uuid",
  "item_description": "string",
  "scheduled_at": "ISO8601 datetime",
  "address": {},
  "otp": "6-digit string",
  "status": "pending",
  "created_at": "ISO8601 datetime"
}
```

---

### GET /pickups/:pickup_id
Fetch a single pickup by ID.

**Response `200`:**
```json
{
  "pickup_id": "uuid",
  "user_id": "uuid",
  "collector_id": "uuid",
  "item_description": "string",
  "scheduled_at": "ISO8601 datetime",
  "address": {},
  "otp": "6-digit string",
  "status": "pending | accepted | in_transit | completed | cancelled",
  "created_at": "ISO8601 datetime",
  "updated_at": "ISO8601 datetime"
}
```

---

### PATCH /pickups/:pickup_id/accept
Collector accepts a pending pickup.

**Response `200`:**
```json
{
  "pickup_id": "uuid",
  "status": "accepted"
}
```

---

### POST /pickups/:pickup_id/verify-otp
Verify OTP at handoff. Triggers EcoPoints award on success.

**Request Body:**
```json
{
  "otp": "string"
}
```

**Response `200`:**
```json
{
  "pickup_id": "uuid",
  "status": "completed",
  "eco_points_awarded": 75,
  "user_total_points": 150
}
```

**Error `400` (invalid/expired OTP):**
```json
{
  "error": "INVALID_OTP",
  "message": "OTP is invalid or has expired."
}
```

---

### PATCH /pickups/:pickup_id/cancel
Cancel a pickup (user or collector).

**Request Body:**
```json
{
  "reason": "string"
}
```

**Response `200`:**
```json
{
  "pickup_id": "uuid",
  "status": "cancelled"
}
```

---

## EcoPoints / Wallet

### GET /users/:user_id/wallet
**Response `200`:**
```json
{
  "user_id": "uuid",
  "eco_points_balance": 225,
  "total_pickups_completed": 3,
  "total_co2_saved_kg": 12.6
}
```

---

## Impact Dashboard

### GET /dashboard/user/:user_id
**Response `200`:**
```json
{
  "user_id": "uuid",
  "total_items_recycled": 5,
  "total_co2_saved_kg": 21.0,
  "eco_points_balance": 375,
  "leaderboard_rank": 42
}
```

### GET /dashboard/global
**Response `200`:**
```json
{
  "total_pickups_completed": 1024,
  "total_co2_saved_kg": 4300.5,
  "top_users": [
    { "user_id": "uuid", "name": "string", "eco_points": 750 }
  ]
}
```

---

## Error Format

All errors follow a consistent envelope:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable description."
}
```

Common error codes: `UNAUTHORIZED`, `NOT_FOUND`, `VALIDATION_ERROR`, `INVALID_OTP`, `OTP_EXPIRED`, `INTERNAL_ERROR`.
