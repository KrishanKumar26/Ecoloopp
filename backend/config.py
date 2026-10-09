"""
Configuration management for EcoLoop Backend.
Loads environment variables and provides application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "127.0.0.1")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "ecoloop_dev")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")

    # Application Settings
    ENV: str = os.getenv("ENV", "development")

    # JWT Authentication Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    @property
    def DATABASE_URL(self) -> str:
        """
        Construct the async PostgreSQL connection URL.
        Format: postgresql+asyncpg://user:password@host:port/database
        """
        if not self.DATABASE_USER:
            raise ValueError(
                "DATABASE_USER not set. Please configure your .env file."
            )
        if not self.DATABASE_PASSWORD:
            raise ValueError(
                "DATABASE_PASSWORD not set. Please configure your .env file."
            )

        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    def is_configured(self) -> bool:
        """Check if database credentials are configured."""
        return bool(self.DATABASE_USER and self.DATABASE_PASSWORD)


# Global settings instance
settings = Settings()
