# EcoLoop Frontend

Next.js web application for the EcoLoop e-waste recycling platform.

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Package Manager:** npm

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          — Root layout with metadata
│   ├── page.tsx            — Home page with hero, features, and dashboard preview
│   ├── globals.css         — Global styles and Tailwind directives
│   ├── scan/
│   │   └── page.tsx        — E-waste scanning page (placeholder)
│   ├── pickups/
│   │   └── page.tsx        — Pickup tracking page (sample data)
│   └── impact/
│       └── page.tsx        — Environmental impact dashboard (sample data)
├── components/
│   ├── Navigation.tsx      — Main navigation bar
│   ├── Footer.tsx          — Site footer
│   ├── StatCard.tsx        — Reusable stat card component
│   └── FeatureCard.tsx     — Reusable feature card component
├── public/                 — Static assets (created automatically)
└── [config files]          — Next.js, TypeScript, Tailwind, ESLint configs
```

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
```

### Start Production Server

```bash
npm start
```

### Lint Code

```bash
npm run lint
```

## Design System

### Colors

- **Primary (Green):** `eco-green-*` scale (50-900) for sustainability theme
- **Semantic:** Blue, purple, orange for different stat types
- **Neutrals:** Gray scale for text and backgrounds

### Typography

- **Font:** Inter (Google Fonts)
- **Headings:** Bold, clear hierarchy
- **Body:** 14-16px, leading-relaxed for readability

### Components

All components are located in `/components` and follow TypeScript prop interfaces.

## Current Status

### ✅ Implemented

- Responsive navigation with logo and tagline
- Hero section explaining the problem and solution
- Feature cards showcasing the 9-step MVP flow
- Dashboard preview with sample EcoPoints, pickups, CO₂ data
- Impact page with personal stats and leaderboard
- Pickups page with status tracking (sample data)
- Footer with branding
- Full responsive design (mobile, tablet, desktop)
- Demo status banners to clearly label sample data

### 🚧 Not Yet Implemented

- Authentication (login/register)
- Image upload and camera integration
- Backend API integration
- Real-time pickup status updates
- OTP verification flow
- EcoPoints redemption
- User profile management

## API Integration Notes

When connecting to the backend, use these endpoints (from `API.md`):

- `POST /ai/classify` — Upload image for e-waste classification
- `GET /recyclers` — Fetch nearby recyclers
- `POST /pickups` — Create pickup request
- `GET /pickups/:pickup_id` — Get pickup details
- `POST /pickups/:pickup_id/verify-otp` — Verify OTP (awards 75 EcoPoints)
- `GET /users/:user_id/wallet` — Get EcoPoints balance
- `GET /dashboard/user/:user_id` — Get personal impact stats
- `GET /dashboard/global` — Get global community stats

## Environment Variables

Create a `.env.local` file for environment-specific configuration:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.ecoloop.app/v1
```

## License

MIT — Hackathon project
