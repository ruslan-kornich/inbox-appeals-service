from fastapi import APIRouter

public_router = APIRouter()


@public_router.get("/", tags=["Health Check"])
async def root() -> dict:
    """Root endpoint."""
    return {"message": "OK"}
