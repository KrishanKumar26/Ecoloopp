"""
Database connection and session management for EcoLoop.
Uses SQLAlchemy 2.0 with asyncpg for async PostgreSQL operations.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from config import settings

# Create the async database engine
# NullPool is used to avoid connection pool issues during development
engine = None
async_session_maker = None

# Base class for SQLAlchemy models
Base = declarative_base()


def init_db():
    """
    Initialize the database engine and session maker.
    Called on application startup.
    """
    global engine, async_session_maker

    if not settings.is_configured():
        print("⚠️  Database credentials not configured. Skipping database initialization.")
        return

    try:
        # Create async engine with connection pooling
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=True if settings.ENV == "development" else False,
            poolclass=NullPool,  # Simple pool for development
        )

        # Create async session factory
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        print(f"✓ Database engine initialized for {settings.DATABASE_NAME}")

    except Exception as e:
        print(f"✗ Failed to initialize database engine: {e}")
        raise


async def get_db() -> AsyncSession:
    """
    Dependency function to get a database session.
    Used with FastAPI's dependency injection.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            # Use db session here
    """
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_database_connection() -> dict:
    """
    Check if the database connection is working.
    Returns a dict with status information, safe for API responses.

    Returns:
        dict: Connection status with keys 'connected', 'message', and optionally 'error'
    """
    if not settings.is_configured():
        return {
            "connected": False,
            "message": "Database credentials not configured",
            "error": "Missing DATABASE_USER or DATABASE_PASSWORD in .env file",
        }

    if engine is None:
        return {
            "connected": False,
            "message": "Database engine not initialized",
            "error": "Call init_db() before checking connection",
        }

    try:
        # Attempt to execute a simple query
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {
            "connected": True,
            "message": f"Connected to {settings.DATABASE_NAME}",
            "database": settings.DATABASE_NAME,
            "host": settings.DATABASE_HOST,
        }

    except Exception as e:
        # Return safe error message without exposing credentials
        error_msg = str(e)
        # Remove any password from error messages
        if settings.DATABASE_PASSWORD in error_msg:
            error_msg = error_msg.replace(settings.DATABASE_PASSWORD, "***")

        return {
            "connected": False,
            "message": "Database connection failed",
            "error": f"Connection error: {type(e).__name__}",
            "details": error_msg if settings.ENV == "development" else None,
        }


async def close_db():
    """
    Close the database engine and clean up connections.
    Called on application shutdown.
    """
    global engine
    if engine is not None:
        await engine.dispose()
        print("✓ Database connections closed")
