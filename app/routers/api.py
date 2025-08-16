from fastapi import APIRouter

from app.routers.routes import auth

public_router = APIRouter()

public_router.include_router(
    auth.router,
    prefix="/auth", tags=["Auth"],
)


@public_router.get("/", tags=["Health Check"])
async def root() -> dict:
    """Root endpoint."""
    return {"message": "OK"}
