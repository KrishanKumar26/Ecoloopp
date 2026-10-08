# EcoLoop — Team

**Hackathon:** EcoLoop  
**Theme:** Turn Waste Into Value

---

## Team Members

| Name | Role | Responsibilities |
|------|------|-----------------|
| TBD  | Full-Stack Lead | Architecture, backend APIs, database |
| TBD  | Frontend Developer | React Native / Next.js UI, UX flow |
| TBD  | AI / ML Engineer | Classification service, GPT-4o integration |
| TBD  | DevOps / Infra | Deployment, CI/CD, environment setup |

> Update this table with actual team member names and GitHub handles.

---

## Roles & Ownership

### Full-Stack Lead
- Overall system architecture decisions
- `backend/` — Express API, route handlers, auth, OTP logic
- Database schema (`DATABASE.md`) and migrations
- Integration between backend and AI service

### Frontend Developer
- `frontend/` — All screens and navigation
- Image upload flow and camera integration
- EcoPoints wallet and impact dashboard UI
- Recycler selection and scheduling screens

### AI / ML Engineer
- `ai/` — FastAPI classification service
- GPT-4o Vision prompt engineering
- Safety tips library and CO₂ calculation logic
- Model evaluation and accuracy benchmarking

### DevOps / Infra
- Docker Compose for local development
- Environment variables and secrets management
- Cloud deployment (Render / Railway / AWS / GCP)
- CI/CD pipeline setup

---

## Communication

- **Stand-up:** Every 4 hours during hackathon
- **Blockers:** Flag immediately in team chat
- **Branching:** `main` (stable) → feature branches per person
- **PR Review:** At least one other team member must approve

---

## Git Workflow

```
main
 ├── feat/backend-auth
 ├── feat/ai-classify
 ├── feat/frontend-upload
 └── feat/pickup-flow
```

- Commit message format: `type(scope): description`
  - e.g., `feat(api): add OTP verification endpoint`
  - e.g., `fix(ai): handle unreadable image error`
  - e.g., `docs(readme): update setup instructions`

---

## Environment Setup Checklist

- [ ] Node.js ≥ 20
- [ ] Python ≥ 3.11
- [ ] PostgreSQL ≥ 15
- [ ] Redis ≥ 7
- [ ] Docker & Docker Compose (optional but recommended)
- [ ] Environment variables configured (`.env` files — never commit these)

---

## Key Decisions Log

| Date       | Decision                              | Rationale                            |
|------------|---------------------------------------|--------------------------------------|
| 2026-10-08 | Use GPT-4o Vision for AI (MVP)        | Fastest integration for hackathon    |
| 2026-10-08 | PostgreSQL as primary DB              | Relational data, strong UUID support |
| 2026-10-08 | 75 EcoPoints per completed pickup     | Simple, memorable reward structure   |
| 2026-10-08 | OTP valid for 30 minutes              | Balance between security and UX      |
