# EcoLoop Backend

Python FastAPI backend for the EcoLoop e-waste recycling platform.

## Tech Stack

- **Framework:** FastAPI 0.115.4
- **Server:** Uvicorn (ASGI server)
- **Language:** Python 3.11+

## Project Structure

```
backend/
├── main.py              — FastAPI application with health endpoint
├── requirements.txt     — Python dependencies
├── README.md           — This file
└── .gitignore          — Git ignore rules for Python
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

Check your Python version:
```bash
python3 --version
```

### 1. Create a Virtual Environment

A virtual environment keeps your project dependencies isolated from your system Python.

**On macOS/Linux:**
```bash
cd backend
python3 -m venv venv
```

**On Windows:**
```bash
cd backend
python -m venv venv
```

### 2. Activate the Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` appear in your terminal prompt, indicating the virtual environment is active.

### 3. Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI — Web framework
- Uvicorn — ASGI server with auto-reload support

### 4. Start the Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Command breakdown:**
- `main:app` — Run the `app` instance from `main.py`
- `--reload` — Auto-reload on code changes (development only)
- `--host 0.0.0.0` — Listen on all network interfaces
- `--port 8000` — Run on port 8000

The server will start at: **http://localhost:8000**

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5. Test the Health Endpoint

**Option 1: Browser**
Open http://localhost:8000/health in your browser.

**Option 2: curl**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "ecoloop-backend",
  "timestamp": "2026-10-08T12:34:56.789Z"
}
```

### 6. View API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These interfaces let you test endpoints directly from your browser.

## Available Endpoints

### GET /
Root endpoint with basic API information.

**Response:**
```json
{
  "message": "EcoLoop API",
  "version": "1.0.0",
  "status": "running"
}
```

### GET /health
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "ecoloop-backend",
  "timestamp": "2026-10-08T12:34:56.789Z"
}
```

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (Next.js frontend development server)
- `http://127.0.0.1:3000` (alternative localhost)

This allows the frontend to make API calls during development.

## Deactivating the Virtual Environment

When you're done working, deactivate the virtual environment:

```bash
deactivate
```

## Troubleshooting

### Port already in use
If port 8000 is already taken, use a different port:
```bash
uvicorn main:app --reload --port 8001
```

### ModuleNotFoundError
Make sure your virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### CORS errors in browser
Check that the frontend is running on `http://localhost:3000`. If using a different port, update the `allow_origins` list in `main.py`.

## Next Steps

Future implementation phases will add:
- Database integration (PostgreSQL + Redis)
- Authentication endpoints (JWT + OTP)
- AI classification service integration
- Recycler discovery endpoints
- Pickup scheduling and tracking
- EcoPoints wallet and transactions
- Environmental impact calculations

See the project root documentation for the complete API specification:
- `../API.md` — Full API reference
- `../DATABASE.md` — Database schema
- `../PRD.md` — Product requirements

## License

MIT — Hackathon project
