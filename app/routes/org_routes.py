"""
API routes for organization management operations.
Defines endpoints for creating, reading, updating, and deleting organizations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List

from app.database.connection import get_database
from app.services.org_service import OrganizationService
from app.models.org_models import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationDelete,
    OrganizationResponse
)
from app.models.auth_models import CurrentAdmin
from app.routes.auth_routes import get_current_admin


router = APIRouter(
    prefix="/org",
    tags=["Organizations"]
)


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization"
)
async def create_organization(
    org_data: OrganizationCreate,
    db=Depends(get_database)
) -> Dict[str, Any]:
    """
    Create a new organization with admin user.
    
    This endpoint:
    - Validates organization name uniqueness
    - Creates a new organization-specific collection
    - Creates an admin user with hashed password
    - Stores metadata in master database
    
    **Request Body:**
    - `organization_name`: Unique name (3-50 chars, alphanumeric + underscores)
    - `email`: Admin email address
    - `password`: Admin password (min 6 characters)
    
    **Returns:**
    - Organization metadata with admin info
    
    **Status Codes:**
    - `201`: Organization created successfully
    - `409`: Organization name already exists
    - `400`: Invalid input data
    """
    org_service = OrganizationService(db)
    result = await org_service.create_organization(org_data)
    
    return {
        "success": True,
        "message": "Organization created successfully",
        "data": result
    }


@router.get(
    "/get",
    status_code=status.HTTP_200_OK,
    summary="Get organization by name"
)
async def get_organization(
    organization_name: str = Query(..., description="Organization name to retrieve"),
    db=Depends(get_database)
) -> Dict[str, Any]:
    """
    Retrieve organization metadata by name.
    
    **Query Parameters:**
    - `organization_name`: Name of the organization to retrieve
    
    **Returns:**
    - Organization metadata including:
        - Organization name
        - Collection name
        - Admin email
        - Timestamps
        - Active status
    
    **Status Codes:**
    - `200`: Organization found
    - `404`: Organization not found
    """
    org_service = OrganizationService(db)
    result = await org_service.get_organization(organization_name)
    
    return {
        "success": True,
        "message": "Organization retrieved successfully",
        "data": result
    }


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    summary="List all organizations"
)
async def list_organizations(
    db=Depends(get_database)
) -> Dict[str, Any]:
    """
    Retrieve all organizations from the system.
    
    **Returns:**
    - List of all organization metadata
    
    **Status Codes:**
    - `200`: Organizations retrieved successfully
    """
    org_service = OrganizationService(db)
    result = await org_service.get_all_organizations()
    
    return {
        "success": True,
        "message": f"Retrieved {len(result)} organization(s)",
        "data": result
    }


@router.put(
    "/update",
    status_code=status.HTTP_200_OK,
    summary="Update organization"
)
async def update_organization(
    update_data: OrganizationUpdate,
    current_admin: CurrentAdmin = Depends(get_current_admin),
    db=Depends(get_database)
) -> Dict[str, Any]:
    """
    Update organization information (requires authentication).
    
    This endpoint allows updating:
    - Organization name (creates new collection and migrates data)
    - Admin email
    - Admin password
    
    **Authentication:** Required (Bearer token)
    
    **Request Body:**
    - `old_organization_name`: Current organization name
    - `new_organization_name`: New name (optional)
    - `email`: New admin email (optional)
    - `password`: New admin password (optional)
    
    **Returns:**
    - Updated organization metadata
    
    **Status Codes:**
    - `200`: Organization updated successfully
    - `401`: Unauthorized (invalid token)
    - `403`: Forbidden (can only update own organization)
    - `404`: Organization not found
    - `409`: New organization name already exists
    """
    org_service = OrganizationService(db)
    result = await org_service.update_organization(
        update_data=update_data,
        current_admin_org=current_admin.organization_name
    )
    
    return {
        "success": True,
        "message": "Organization updated successfully",
        "data": result
    }


@router.delete(
    "/delete",
    status_code=status.HTTP_200_OK,
    summary="Delete organization"
)
async def delete_organization(
    delete_data: OrganizationDelete,
    current_admin: CurrentAdmin = Depends(get_current_admin),
    db=Depends(get_database)
) -> Dict[str, Any]:
    """
    Delete an organization and its collection (requires authentication).
    
    This endpoint:
    - Verifies admin permission
    - Drops the organization's collection
    - Removes metadata from master database
    
    **Authentication:** Required (Bearer token)
    
    **Request Body:**
    - `organization_name`: Name of organization to delete
    
    **Returns:**
    - Success message with deleted collection name
    
    **Status Codes:**
    - `200`: Organization deleted successfully
    - `401`: Unauthorized (invalid token)
    - `403`: Forbidden (can only delete own organization)
    - `404`: Organization not found
    """
    org_service = OrganizationService(db)
    result = await org_service.delete_organization(
        delete_data=delete_data,
        current_admin_org=current_admin.organization_name
    )
    
    return {
        "success": True,
        "message": result["message"],
        "data": {
            "organization_name": delete_data.organization_name,
            "deleted_collection": result["deleted_collection"]
        }
    }
