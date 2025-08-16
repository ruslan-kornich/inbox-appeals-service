# app/routes/auth.py
from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import AccessTokenResponse, LoginBody, RegisterUserBody
from app.schemas.users import UserShort
from app.services.auth_service import AuthService

router = APIRouter()
service = AuthService()


@router.post("/register", response_model=UserShort, status_code=status.HTTP_201_CREATED)
async def register_user(body: RegisterUserBody):
    """
    Register a new USER and its citizen profile.
    """
    try:
        user_id, role = await service.register_user(body)
        return UserShort(id=user_id, email=body.email, role=role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/login", response_model=AccessTokenResponse)
async def login(body: LoginBody):
    """
    Login with email and password; returns access token.
    """
    try:
        access = await service.login(email=body.email, password=body.password)
        return AccessTokenResponse(access_token=access)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
