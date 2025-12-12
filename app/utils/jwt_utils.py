"""Small, readable helpers to create and decode JWTs.

These are deliberately straightforward: create a token with an `exp` and
`iat`, and raise HTTP-friendly errors when decoding fails.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError
from app.config.settings import settings
from app.models.auth_models import TokenData
from fastapi import HTTPException, status


class JWTUtils:
    """Tiny wrapper for PyJWT with app-friendly error handling."""

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        now = datetime.utcnow()
        payload = data.copy()

        if expires_delta:
            exp = now + expires_delta
        else:
            exp = now + timedelta(hours=settings.TOKEN_EXPIRE_HOURS)

        payload.update({"exp": exp, "iat": now})

        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return token

    @staticmethod
    def decode_access_token(token: str) -> TokenData:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

            admin_id: str = payload.get("admin_id")
            email: str = payload.get("email")
            organization_name: str = payload.get("organization_name")

            if not (admin_id and email and organization_name):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return TokenData(admin_id=admin_id, email=email, organization_name=organization_name)

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def get_token_expiration_seconds() -> int:
        return settings.TOKEN_EXPIRE_HOURS * 3600
