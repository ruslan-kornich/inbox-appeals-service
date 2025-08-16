from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from app.config.db import DatabaseManager
from app.config.settings import settings
from app.routers.api import public_router
from app.utils.exceptions import BusinessError, business_exception_handler


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """
    Initialize and cleanup the server instance.
    """
    # Setup database connection(s)
    await DatabaseManager.setup(echo=False)

    try:
        yield
    finally:
        # Dispose database connections
        await DatabaseManager.stop()


def create_app() -> FastAPI:
    """
    Fabric app factory. Can configure the FastAPI application.
    """
    instance = FastAPI(
        title="Inbox Appeals Service",
        debug=settings.DEBUG,
        lifespan=lifespan,
        exception_handlers={
            BusinessError: business_exception_handler,
        },
    )

    instance.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    instance.include_router(public_router)

    return instance


app = create_app()

add_pagination(app)
