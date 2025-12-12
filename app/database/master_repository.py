"""
Repository for master database operations.
Handles CRUD operations on the master organization metadata collection.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId


class MasterRepository:
    """
    Repository class for master database operations.
    Manages organization metadata in the master collection.
    """
    
    MASTER_COLLECTION = "master_organizations"
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize repository with database instance.
        
        Args:
            db: Master database instance
        """
        self.db = db
        self.collection: AsyncIOMotorCollection = db[self.MASTER_COLLECTION]
    
    async def create_organization_metadata(
        self,
        organization_name: str,
        collection_name: str,
        admin_id: ObjectId,
        admin_email: str,
        admin_hashed_password: str | None = None
    ) -> Dict[str, Any]:
        """
        Create organization metadata in master collection.
        
        Args:
            organization_name: Unique organization name
            collection_name: Name of the tenant's collection (e.g., 'org_alpha')
            admin_id: ObjectId of the admin user
            admin_email: Email of the admin user
            
        Returns:
            Dict containing the created organization metadata
        """
        org_data = {
            "organization_name": organization_name,
            "collection_name": collection_name,
            "admin_id": admin_id,
            "admin_email": admin_email,
            "admin_hashed_password": admin_hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = await self.collection.insert_one(org_data)
        org_data["_id"] = result.inserted_id
        
        return org_data
    
    async def get_organization_by_name(self, organization_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve organization metadata by name.
        
        Args:
            organization_name: Organization name to search for
            
        Returns:
            Organization metadata dict or None if not found
        """
        return await self.collection.find_one({"organization_name": organization_name})
    
    async def get_organization_by_id(self, org_id: ObjectId) -> Optional[Dict[str, Any]]:
        """
        Retrieve organization metadata by ID.
        
        Args:
            org_id: Organization ObjectId
            
        Returns:
            Organization metadata dict or None if not found
        """
        return await self.collection.find_one({"_id": org_id})
    
    async def check_organization_exists(self, organization_name: str) -> bool:
        """
        Check if organization already exists.
        
        Args:
            organization_name: Organization name to check
            
        Returns:
            True if organization exists, False otherwise
        """
        count = await self.collection.count_documents({"organization_name": organization_name})
        return count > 0
    
    async def update_organization_metadata(
        self,
        old_name: str,
        new_name: str,
        new_collection_name: str,
        admin_email: Optional[str] = None
    ) -> bool:
        """
        Update organization metadata after rename.
        
        Args:
            old_name: Current organization name
            new_name: New organization name
            new_collection_name: New collection name
            admin_email: Optional new admin email
            
        Returns:
            True if update successful, False otherwise
        """
        update_data = {
            "organization_name": new_name,
            "collection_name": new_collection_name,
            "updated_at": datetime.utcnow()
        }
        
        if admin_email:
            update_data["admin_email"] = admin_email
        
        result = await self.collection.update_one(
            {"organization_name": old_name},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def delete_organization_metadata(self, organization_name: str) -> bool:
        """
        Delete organization metadata from master collection.
        
        Args:
            organization_name: Organization name to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        result = await self.collection.delete_one({"organization_name": organization_name})
        return result.deleted_count > 0
    
    async def get_all_organizations(self) -> List[Dict[str, Any]]:
        """
        Retrieve all organizations from master collection.
        
        Returns:
            List of organization metadata dicts
        """
        cursor = self.collection.find({})
        return await cursor.to_list(length=None)
    
    async def get_organization_by_admin_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve organization by admin email.
        
        Args:
            email: Admin email address
            
        Returns:
            Organization metadata dict or None if not found
        """
        return await self.collection.find_one({"admin_email": email})
