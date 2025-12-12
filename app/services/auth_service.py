"""Authentication service: simple, readable business logic.

This module contains the small amount of glue needed to turn requests
into tokens. It is intentionally straightforward so reviewers can follow
the behavior without digging through helpers.
"""

from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.database.master_repository import MasterRepository
from app.models.auth_models import LoginRequest, TokenResponse
from app.utils.hash_utils import HashUtils
from app.utils.jwt_utils import JWTUtils


class AuthService:
    """Authentication-related operations.

    Only a couple of methods are exposed: `login_admin` and `verify_admin_access`.
    Keep the logic local and clear.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.master_repo = MasterRepository(db)

    async def login_admin(self, login_data: LoginRequest) -> TokenResponse:
        """Authenticate an admin and return a JWT response.

        Steps:
        - find the owning organization by admin email (master metadata)
        - load the admin row from the tenant collection
        - verify the password and activity flag
        - build and return a TokenResponse
        """
        org_doc = await self.master_repo.get_organization_by_admin_email(login_data.email)

        if not org_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # tenant collection where admin lives
        collection_name = org_doc["collection_name"]
        org_coll = self.db[collection_name]

        admin_user = await org_coll.find_one({"email": login_data.email})
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # password check
        if not HashUtils.verify_password(login_data.password, admin_user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not admin_user.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin account is inactive")

        token_data = {
            "admin_id": str(admin_user["_id"]),
            "email": admin_user["email"],
            "organization_name": org_doc["organization_name"],
        }

        access_token = JWTUtils.create_access_token(data=token_data)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=JWTUtils.get_token_expiration_seconds(),
            admin_email=admin_user["email"],
            organization_name=org_doc["organization_name"],
        )

    async def verify_admin_access(self, admin_id: str, organization_name: str) -> Dict[str, Any]:
        """Ensure the admin represented by `admin_id` belongs to `organization_name`.

        Returns the admin document when checks pass.
        """
        org_doc = await self.master_repo.get_organization_by_name(organization_name)
        if not org_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Organization not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        org_coll = self.db[org_doc["collection_name"]]

        from bson import ObjectId
        admin_user = await org_coll.find_one({"_id": ObjectId(admin_id)})
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not admin_user.get("is_active", True):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin account is inactive")

        return admin_user
