"""
Configuration settings for the FastAPI application.
Loads environment variables and provides typed configuration access.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        MONGO_URL: MongoDB connection string
        MASTER_DB_NAME: Name of the master database storing organization metadata
        JWT_SECRET: Secret key for JWT token generation
        JWT_ALGORITHM: Algorithm used for JWT encoding/decoding
        TOKEN_EXPIRE_HOURS: Token expiration time in hours
        SERVER_HOST: Host address for the server
        SERVER_PORT: Port number for the server
    """
    
    # MongoDB Configuration
    MONGO_URL: str
    MASTER_DB_NAME: str = "multi_tenant_master"
    
    # JWT Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_HOURS: int = 24
    
    # Server Configuration
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
