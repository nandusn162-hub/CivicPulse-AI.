"""Common FastAPI dependencies for authentication and role‑based access control.

Provides:
- ``get_current_user`` – decodes the JWT, fetches the user from the DB, and returns a ``User`` instance.
- ``require_roles`` – a factory that returns a dependency enforcing that the current user has one of the supplied ``UserRole`` values.

These utilities are used by endpoint routers to protect routes according to the
access matrix defined in the product specification.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import security, config
from app.db.base import get_async_session
from app.models.user import User, UserRole

# OAuth2 scheme extracts the ``Authorization: Bearer <token>`` header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)
) -> User:
    """Decode JWT, load the ``User`` from DB and ensure the account is active.

    The JWT payload is expected to contain ``sub`` (user id) and ``type``.
    ``type`` must be ``access`` for this dependency.
    """
    payload = security.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing sub claim")
    # Load user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")
    return user

def require_roles(*allowed_roles: UserRole):
    """Dependency factory that ensures the current user has one of ``allowed_roles``.

    Usage example:
    ```
    @router.get("/admin")
    async def admin_view(current_user: User = Depends(require_roles(UserRole.ADMIN))):
        ...
    ```
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker
