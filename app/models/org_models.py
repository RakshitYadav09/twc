"""
Pydantic models for organization-related operations.
Defines request/response schemas for organization endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class OrganizationCreate(BaseModel):
    """
    Schema for creating a new organization.
    
    Attributes:
        organization_name: Unique name for the organization (alphanumeric and underscores)
        email: Admin email address
        password: Admin password (minimum 6 characters)
    """
    
    organization_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Organization name (3-50 characters, alphanumeric and underscores only)"
    )
    email: str = Field(..., description="Admin email address")
    password: str = Field(..., min_length=6, description="Admin password (minimum 6 characters)")
    
    @validator('organization_name')
    def validate_org_name(cls, v):
        """Validate organization name format."""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Organization name must contain only alphanumeric characters and underscores')
        return v.lower()
    
    @validator('email')
    def validate_email(cls, v):
        """Basic email validation."""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()


class OrganizationUpdate(BaseModel):
    """
    Schema for updating an organization.
    
    Attributes:
        old_organization_name: Current organization name
        new_organization_name: New organization name (optional)
        email: New admin email (optional)
        password: New admin password (optional)
    """
    
    old_organization_name: str = Field(..., description="Current organization name")
    new_organization_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="New organization name"
    )
    email: Optional[str] = Field(None, description="New admin email")
    password: Optional[str] = Field(None, min_length=6, description="New admin password")
    
    @validator('new_organization_name')
    def validate_new_org_name(cls, v):
        """Validate new organization name format."""
        if v and not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Organization name must contain only alphanumeric characters and underscores')
        return v.lower() if v else v
    
    @validator('email')
    def validate_email(cls, v):
        """Basic email validation."""
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower() if v else v


class OrganizationDelete(BaseModel):
    """
    Schema for deleting an organization.
    
    Attributes:
        organization_name: Name of the organization to delete
    """
    
    organization_name: str = Field(..., description="Organization name to delete")


class OrganizationResponse(BaseModel):
    """
    Schema for organization response data.
    
    Attributes:
        organization_name: Organization name
        collection_name: Associated collection name
        admin_email: Admin email address
        created_at: Creation timestamp
        updated_at: Last update timestamp
        is_active: Active status
    """
    
    organization_name: str
    collection_name: str
    admin_email: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
