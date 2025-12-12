"""
API routes for authentication operations.
Defines endpoints for admin login and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from app.database.connection import get_database
from app.services.auth_service import AuthService
from app.models.auth_models import LoginRequest, TokenResponse, CurrentAdmin
from app.utils.jwt_utils import JWTUtils


router = APIRouter(
    prefix="/admin",
    tags=["Authentication"]
)

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_database)
) -> CurrentAdmin:
    """
    Dependency to get current authenticated admin from JWT token.

    This dependency:
    - Extracts JWT token from Authorization header
    - Validates and decodes token
    - Verifies admin exists and is active

    Args:
        credentials: HTTP bearer token credentials
        db: Database instance

    Returns:
        CurrentAdmin object with admin info

    Raises:
        HTTPException: If token is invalid or admin not found
    """
    token = credentials.credentials

    # Decode and validate token
    token_data = JWTUtils.decode_access_token(token)

    # Verify admin access
    auth_service = AuthService(db)
    await auth_service.verify_admin_access(
        admin_id=token_data.admin_id,
        organization_name=token_data.organization_name
    )

    # Return current admin info
    return CurrentAdmin(
        admin_id=token_data.admin_id,
        email=token_data.email,
        organization_name=token_data.organization_name
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Admin login"
)
async def login_admin(
    login_data: LoginRequest,
    db=Depends(get_database)
) -> TokenResponse:
    """
    Authenticate admin and generate JWT access token.
    
    This endpoint:
    - Validates admin credentials
    - Verifies password using bcrypt
    - Generates JWT token with admin and organization info
    
    **Request Body:**
    - `email`: Admin email address
    - `password`: Admin password
    
    **Returns:**
    - JWT access token
    - Token type (bearer)
    - Token expiration time (seconds)
    - Admin email
    - Organization name
    
    **Status Codes:**
    - `200`: Login successful
    - `401`: Invalid credentials
    - `403`: Admin account inactive
    
    **Example Response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "expires_in": 86400,
        "admin_email": "admin@example.com",
        "organization_name": "alpha"
    }
    ```
    """
    auth_service = AuthService(db)
    token_response = await auth_service.login_admin(login_data)
    
    return token_response


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get current admin info"
)
async def get_current_admin_info(
    current_admin: CurrentAdmin = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Get information about the currently authenticated admin.
    
    **Authentication:** Required (Bearer token)
    
    **Returns:**
    - Admin ID
    - Email address
    - Organization name
    
    **Status Codes:**
    - `200`: Admin info retrieved successfully
    - `401`: Unauthorized (invalid or expired token)
    
    **Example Response:**
    ```json
    {
        "success": true,
        "message": "Current admin info retrieved",
        "data": {
            "admin_id": "507f1f77bcf86cd799439011",
            "email": "admin@example.com",
            "organization_name": "alpha"
        }
    }
    ```
    """
    return {
        "success": True,
        "message": "Current admin info retrieved",
        "data": {
            "admin_id": current_admin.admin_id,
            "email": current_admin.email,
            "organization_name": current_admin.organization_name
        }
    }

