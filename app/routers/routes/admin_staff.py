
from fastapi import APIRouter, Depends, HTTPException, status

from app.models import UserRole
from app.schemas.users import CreateStaffBody, UserShort
from app.security.dependencies import require_roles
from app.services.admin_service import AdminService

router = APIRouter()
service = AdminService()


@router.get("", response_model=list[UserShort], dependencies=[Depends(require_roles(UserRole.ADMIN))])
async def list_staff():
    """
    List all staff users (admin only).
    """
    users = await service.list_staff()
    return [UserShort(id=str(u.id), email=u.email, role=u.role) for u in users]


@router.post("", response_model=UserShort, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.ADMIN))])
async def create_staff(body: CreateStaffBody):
    """
    Create a staff user (admin only).
    """
    try:
        user = await service.create_staff(email=body.email, password=body.password)
        return UserShort(id=str(user.id), email=user.email, role=user.role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
