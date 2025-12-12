"""
Service layer for organization management operations.
Implements business logic for creating, updating, and managing organizations.
"""

from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException, status

from app.database.master_repository import MasterRepository
from app.models.org_models import OrganizationCreate, OrganizationUpdate, OrganizationDelete
from app.utils.hash_utils import HashUtils


class OrganizationService:
    """
    Service class for organization-related business logic.
    Handles multi-tenant collection creation and management.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize the organization service.
        
        Args:
            db: Master database instance
        """
        self.db = db
        self.master_repo = MasterRepository(db)
    
    async def create_organization(
        self,
        org_data: OrganizationCreate
    ) -> Dict[str, Any]:
        """
        Create a new organization with its own collection.
        
        This method:
        1. Validates organization name is unique
        2. Creates admin user with hashed password
        3. Creates organization-specific collection
        4. Stores metadata in master database
        
        Args:
            org_data: Organization creation data
            
        Returns:
            Dict containing organization metadata and admin info
            
        Raises:
            HTTPException: If organization already exists
        """
        # Check if organization already exists
        exists = await self.master_repo.check_organization_exists(org_data.organization_name)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Organization '{org_data.organization_name}' already exists"
            )
        
        # Generate collection name for this organization
        collection_name = f"org_{org_data.organization_name}"
        
        # Hash the admin password
        hashed_password = HashUtils.hash_password(org_data.password)
        
        # Create admin user document
        admin_user = {
            "email": org_data.email,
            "hashed_password": hashed_password,
            "organization_name": org_data.organization_name,
            "is_active": True
        }
        
        # Store admin in the organization's collection
        org_collection = self.db[collection_name]
        admin_result = await org_collection.insert_one(admin_user)
        admin_id = admin_result.inserted_id
        
        # Create organization metadata in master collection
        org_metadata = await self.master_repo.create_organization_metadata(
            organization_name=org_data.organization_name,
            collection_name=collection_name,
            admin_id=admin_id,
            admin_email=org_data.email,
            admin_hashed_password=hashed_password
        )
        
        # Prepare response
        response_data = {
            "organization_name": org_data.organization_name,
            "collection_name": collection_name,
            "admin_email": org_data.email,
            "admin_id": str(admin_id),
            "created_at": org_metadata["created_at"],
            "is_active": org_metadata["is_active"]
        }
        
        return response_data
    
    async def get_organization(self, organization_name: str) -> Dict[str, Any]:
        """
        Retrieve organization metadata by name.
        
        Args:
            organization_name: Organization name to retrieve
            
        Returns:
            Organization metadata dict
            
        Raises:
            HTTPException: If organization not found
        """
        org = await self.master_repo.get_organization_by_name(organization_name)
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{organization_name}' not found"
            )
        
        # Convert ObjectId to string for JSON serialization
        org["_id"] = str(org["_id"])
        org["admin_id"] = str(org["admin_id"])
        
        return org
    
    async def update_organization(
        self,
        update_data: OrganizationUpdate,
        current_admin_org: str
    ) -> Dict[str, Any]:
        """
        Update organization information.
        
        This method:
        1. Validates permissions
        2. Creates new collection if name changes
        3. Copies data from old collection to new
        4. Updates admin credentials if provided
        5. Removes old collection
        6. Updates master metadata
        
        Args:
            update_data: Organization update data
            current_admin_org: Organization name of authenticated admin
            
        Returns:
            Updated organization metadata
            
        Raises:
            HTTPException: If validation fails or unauthorized
        """
        old_name = update_data.old_organization_name
        new_name = update_data.new_organization_name or old_name
        
        # Check if admin is authorized to update this organization
        if current_admin_org != old_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own organization"
            )
        
        # Get existing organization
        org = await self.master_repo.get_organization_by_name(old_name)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{old_name}' not found"
            )
        
        # If name is changing, check new name doesn't exist
        if new_name != old_name:
            exists = await self.master_repo.check_organization_exists(new_name)
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Organization '{new_name}' already exists"
                )
        
        old_collection_name = org["collection_name"]
        new_collection_name = f"org_{new_name}"
        
        # Get old collection
        old_collection = self.db[old_collection_name]
        
        # If name changed, create new collection and copy data
        if new_name != old_name:
            new_collection = self.db[new_collection_name]
            
            # Copy all documents from old collection to new
            async for document in old_collection.find({}):
                if update_data.email:
                    document["email"] = update_data.email
                if update_data.password:
                    document["hashed_password"] = HashUtils.hash_password(update_data.password)
                if "organization_name" in document:
                    document["organization_name"] = new_name
                
                await new_collection.insert_one(document)
            
            # Drop old collection
            await old_collection.drop()
        else:
            # Update admin in same collection
            if update_data.email or update_data.password:
                update_fields = {}
                if update_data.email:
                    update_fields["email"] = update_data.email
                if update_data.password:
                    update_fields["hashed_password"] = HashUtils.hash_password(update_data.password)
                
                await old_collection.update_one(
                    {"_id": org["admin_id"]},
                    {"$set": update_fields}
                )
        
        # Update master metadata
        await self.master_repo.update_organization_metadata(
            old_name=old_name,
            new_name=new_name,
            new_collection_name=new_collection_name,
            admin_email=update_data.email
        )
        
        # Get updated organization
        updated_org = await self.get_organization(new_name)
        
        return updated_org
    
    async def delete_organization(
        self,
        delete_data: OrganizationDelete,
        current_admin_org: str
    ) -> Dict[str, str]:
        """
        Delete an organization and its collection.
        
        Args:
            delete_data: Organization deletion data
            current_admin_org: Organization name of authenticated admin
            
        Returns:
            Success message dict
            
        Raises:
            HTTPException: If validation fails or unauthorized
        """
        org_name = delete_data.organization_name
        
        # Check if admin is authorized to delete this organization
        if current_admin_org != org_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own organization"
            )
        
        # Get organization metadata
        org = await self.master_repo.get_organization_by_name(org_name)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{org_name}' not found"
            )
        
        # Drop the organization's collection
        collection_name = org["collection_name"]
        await self.db[collection_name].drop()
        
        # Delete organization metadata from master
        await self.master_repo.delete_organization_metadata(org_name)
        
        return {
            "message": f"Organization '{org_name}' deleted successfully",
            "deleted_collection": collection_name
        }
    
    async def get_all_organizations(self) -> list[Dict[str, Any]]:
        """
        Retrieve all organizations from master database.
        
        Returns:
            List of organization metadata dicts
        """
        orgs = await self.master_repo.get_all_organizations()
        
        # Convert ObjectIds to strings
        for org in orgs:
            org["_id"] = str(org["_id"])
            org["admin_id"] = str(org["admin_id"])
        
        return orgs
