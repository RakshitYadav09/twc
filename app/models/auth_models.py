"""
Pydantic models for authentication operations.
Defines request/response schemas for login and token operations.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
import re


class LoginRequest(BaseModel):
    """
    Schema for admin login request.
    
    Attributes:
        email: Admin email address
        password: Admin password
    """
    
    email: str = Field(..., description="Admin email address")
    password: str = Field(..., description="Admin password")
    
    @validator('email')
    def validate_email(cls, v):
        """Basic email validation."""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()


class TokenResponse(BaseModel):
    """
    Schema for JWT token response.
    
    Attributes:
        access_token: JWT access token
        token_type: Token type (always 'bearer')
        expires_in: Token expiration time in seconds
        admin_email: Authenticated admin email
        organization_name: Associated organization name
    """
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    admin_email: str = Field(..., description="Admin email address")
    organization_name: str = Field(..., description="Organization name")


class TokenData(BaseModel):
    """
    Schema for decoded JWT token data.
    
    Attributes:
        admin_id: Admin user ID
        email: Admin email address
        organization_name: Associated organization name
    """
    
    admin_id: str = Field(..., description="Admin user ID")
    email: str = Field(..., description="Admin email address")
    organization_name: str = Field(..., description="Organization name")


class CurrentAdmin(BaseModel):
    """
    Schema for current authenticated admin.
    
    Attributes:
        admin_id: Admin user ID
        email: Admin email address
        organization_name: Associated organization name
    """
    
    admin_id: str
    email: str
    organization_name: str
