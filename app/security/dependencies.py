from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models import UserRole
from app.repositories.users_repository import UserRepository

from .jwt import decode_token

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> tuple[str, UserRole]:
    """
    Extract current user id and role from JWT access token.
    """
    try:
        payload = decode_token(credentials.credentials)
        user_id = str(payload.get("sub"))
        role = UserRole(payload.get("role"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Optionally ensure user still exists (cheap guard)
    repo = UserRepository()
    user = await repo.get_by_id(id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user_id, role


def require_roles(*allowed_roles: UserRole) -> Callable:
    """
    Dependency factory to enforce role-based access on route handlers.
    """

    async def _require(user_and_role: Annotated[tuple[str, UserRole], Depends(get_current_user)]) -> tuple[
        str, UserRole]:
        _, role = user_and_role
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user_and_role

    return _require
