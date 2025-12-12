"""
Pydantic models for admin user operations.
Defines schemas for admin user data and storage.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class AdminUser(BaseModel):
    """
    Schema for admin user in database.
    
    Attributes:
        email: Admin email address
        hashed_password: Bcrypt hashed password
        organization_name: Associated organization name
        created_at: User creation timestamp
        is_active: Active status
    """
    
    email: str
    hashed_password: str
    organization_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }


class AdminUserInDB(AdminUser):
    """
    Extended schema for admin user with database ID.
    
    Attributes:
        id: MongoDB ObjectId as string
    """
    
    id: str = Field(alias="_id")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        populate_by_name = True


class AdminUserResponse(BaseModel):
    """
    Schema for admin user response (without password).
    
    Attributes:
        email: Admin email address
        organization_name: Associated organization name
        created_at: User creation timestamp
        is_active: Active status
    """
    
    email: str
    organization_name: str
    created_at: datetime
    is_active: bool
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
