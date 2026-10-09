"""
EcoLoop Backend API
A FastAPI application for the EcoLoop e-waste recycling platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager

from database import init_db, close_db, check_database_connection
from routers import auth, classification, pickup, ecopoints


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database connection
    print("🚀 Starting EcoLoop Backend...")
    try:
        init_db()
    except Exception as e:
        print(f"⚠️  Warning: Database initialization failed: {e}")
        print("   API will run but database endpoints will not work.")

    yield

    # Shutdown: Close database connections
    print("🛑 Shutting down EcoLoop Backend...")
    await close_db()


# Create FastAPI application instance with lifespan manager
app = FastAPI(
    title="EcoLoop API",
    description="Backend API for EcoLoop e-waste recycling platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for local frontend development
# This allows the frontend running at http://localhost:3000 to make API requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "http://127.0.0.1:3000",  # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# ============================================================================
# Register Routers
# ============================================================================

# Include authentication router
app.include_router(auth.router)

# Include classification router
app.include_router(classification.router)

# Include pickup router
app.include_router(pickup.router)

# Include ecopoints router
app.include_router(ecopoints.router)


# ============================================================================
# Root Endpoints
# ============================================================================


@app.get("/")
async def root():
    """
    Root endpoint - provides basic API information.
    """
    return {
        "message": "EcoLoop API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint - verifies that the backend is running.
    Used for monitoring and deployment health checks.
    """
    return {
        "status": "healthy",
        "service": "ecoloop-backend",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/health/db")
async def database_health_check():
    """
    Database health check endpoint.
    Tests the PostgreSQL connection and returns status information.

    Returns:
        dict: Connection status with safe error messages (no credentials exposed)
    """
    result = await check_database_connection()

    # Set appropriate HTTP status based on connection state
    status_code = 200 if result.get("connected") else 503

    return {
        "status": "healthy" if result.get("connected") else "unhealthy",
        "database": result,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
