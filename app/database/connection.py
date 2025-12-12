"""
Database connection management using Motor async MongoDB driver.
Provides singleton database client and helper functions.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings
from typing import Optional


class DatabaseConnection:
    """
    Singleton class to manage MongoDB connection.
    Ensures only one client instance exists throughout the application lifecycle.
    """
    
    _client: Optional[AsyncIOMotorClient] = None
    _master_db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls) -> None:
        """
        Establish connection to MongoDB.
        Creates client and master database references.
        """
        if cls._client is None:
            cls._client = AsyncIOMotorClient(settings.MONGO_URL)
            cls._master_db = cls._client[settings.MASTER_DB_NAME]
            print(f"✅ Connected to MongoDB: {settings.MASTER_DB_NAME}")
    
    @classmethod
    async def disconnect(cls) -> None:
        """
        Close MongoDB connection.
        Should be called on application shutdown.
        """
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._master_db = None
            print("🔌 Disconnected from MongoDB")
    
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """
        Get the MongoDB client instance.
        
        Returns:
            AsyncIOMotorClient: MongoDB async client
            
        Raises:
            RuntimeError: If connection not established
        """
        if cls._client is None:
            raise RuntimeError("Database connection not established. Call connect() first.")
        return cls._client
    
    @classmethod
    def get_master_db(cls) -> AsyncIOMotorDatabase:
        """
        Get the master database instance.
        
        Returns:
            AsyncIOMotorDatabase: Master database for organization metadata
            
        Raises:
            RuntimeError: If connection not established
        """
        if cls._master_db is None:
            raise RuntimeError("Database connection not established. Call connect() first.")
        return cls._master_db
    
    @classmethod
    def get_tenant_db(cls, collection_name: str) -> AsyncIOMotorDatabase:
        """
        Get a tenant-specific database collection.
        
        Args:
            collection_name: Name of the tenant's collection (e.g., 'org_alpha')
            
        Returns:
            AsyncIOMotorDatabase: Database instance with tenant collection
        """
        client = cls.get_client()
        # All tenant collections are in the master database
        return cls.get_master_db()


# Convenience functions for dependency injection
async def get_database() -> AsyncIOMotorDatabase:
    """
    FastAPI dependency to get master database.
    
    Returns:
        AsyncIOMotorDatabase: Master database instance
    """
    return DatabaseConnection.get_master_db()


async def get_client() -> AsyncIOMotorClient:
    """
    FastAPI dependency to get MongoDB client.
    
    Returns:
        AsyncIOMotorClient: MongoDB client instance
    """
    return DatabaseConnection.get_client()
