# EcoLoop — Turn Waste Into Value ♻️

EcoLoop is a hackathon project that connects households and businesses with certified e-waste recyclers. Users upload a photo of their electronic waste, receive AI-powered identification and safety recommendations, schedule a pickup, and earn EcoPoints for responsible disposal.

---

## Core MVP Flow

```
Image Upload
    ↓
AI E-Waste Identification
    ↓
Safety Recommendation
    ↓
Recycler Selection
    ↓
Pickup Scheduling
    ↓
Collector Acceptance
    ↓
OTP Verification
    ↓
Award 75 EcoPoints
    ↓
Environmental Impact Dashboard
```

---

## Project Structure

```
ecoloop/
├── README.md          — Project overview (this file)
├── PRD.md             — Product Requirements Document
├── API.md             — API reference and field definitions
├── DATABASE.md        — Database schema and entity relationships
├── AI_CONTEXT.md      — AI model context, prompts, and classification guide
├── TEAM.md            — Team roles and responsibilities
├── frontend/          — React Native / Next.js client app
├── backend/           — Node.js / Express API server
├── ai/                — AI classification service (Python / FastAPI)
└── docs/              — Additional documentation and assets
```

---

## Quick Start

> Dependencies are not yet installed. See each sub-directory's README once scaffolding is complete.

---

## Tech Stack (Planned)

| Layer      | Technology              |
|------------|-------------------------|
| Frontend   | React Native / Next.js  |
| Backend    | Node.js + Express       |
| Database   | PostgreSQL + Redis       |
| AI Service | Python + FastAPI         |
| Storage    | AWS S3 / Cloudinary      |
| Auth       | JWT + OTP (SMS)          |

---

## Key Features

- 📸 **AI E-Waste Identification** — camera upload + image classification
- 🔒 **Safety Recommendations** — handling tips per waste category
- 🗺️ **Recycler Matching** — geo-based certified recycler discovery
- 📅 **Pickup Scheduling** — calendar-based slot booking
- ✅ **OTP Verification** — secure handoff confirmation
- 🌱 **EcoPoints** — 75 points awarded per verified pickup
- 📊 **Impact Dashboard** — CO₂ saved, items recycled, leaderboard

---

## License

MIT — built for hackathon purposes.
