from fastapi import APIRouter

from app.routers.routes import admin_analytics, admin_staff, auth, tickets_staff, tickets_user

public_router = APIRouter()
public_router.include_router(
    auth.router,
    prefix="/auth", tags=["Auth"],
)
public_router.include_router(
    admin_analytics.router,
    prefix="/admin/analytics", tags=["Admin Analytics"],
)
public_router.include_router(
    admin_staff.router,
    prefix="/admin/staff", tags=["Admin Staff"],
)
public_router.include_router(
    tickets_staff.router,
    prefix="/staff/tickets", tags=["Staff"],
)
public_router.include_router(
    tickets_user.router,
    prefix="/tickets", tags=["Tickets"],
)


@public_router.get("/", tags=["Health Check"])
async def root() -> dict:
    """Root endpoint."""
    return {"message": "OK"}
