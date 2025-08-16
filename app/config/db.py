from collections.abc import AsyncGenerator
import logging
from typing import Optional

from tortoise import Tortoise, connections
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.transactions import in_transaction

from app.config.settings import settings


def _to_tortoise_dsn(dsn: str) -> str:
    """
    Normalize DSN for Tortoise/asyncpg.

    Tortoise expects 'postgres://...' (async driver inferred).
    This helper converts common SQLAlchemy DSNs to the Tortoise-friendly form.
    """
    if dsn.startswith("postgresql+asyncpg://"):
        return "postgres://" + dsn.split("://", 1)[1]
    if dsn.startswith("postgresql://"):
        return "postgres://" + dsn.split("://", 1)[1]
    if dsn.startswith("postgres+asyncpg://"):
        return "postgres://" + dsn.split("://", 1)[1]
    return dsn


# IMPORTANT:
# - Put all your model modules in "models" list below.
# - Keep "aerich.models" for migrations history table.
TORTOISE_ORM = {
    "connections": {
        "default": _to_tortoise_dsn(settings.ASYNC_DATABASE_URL),
    },
    "apps": {
        "models": {
            # List every module that contains Tortoise models
            # Example: "app.models.user", "app.models.ticket"
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    # Timezone handling similar to your SQLAlchemy server_settings (UTC)
    "use_tz": True,
    "timezone": "UTC",
}


class DatabaseManager:
    """
    Minimal database lifecycle manager for Tortoise ORM.

    - setup(): initialize connections with the configured apps
    - stop(): close all connections

    NOTE:
    * Do NOT call `Tortoise.generate_schemas()` here; Aerich owns schema migrations.
    * Enable SQL logging via `echo=True` or DEBUG to see ORM queries.
    """
    started: bool = False

    @classmethod
    async def setup(cls, *, echo: Optional[bool] = None) -> None:
        """
        Initialize Tortoise connections and ORM apps.
        """
        await Tortoise.init(config=TORTOISE_ORM)
        cls.started = True

        # Optional SQL debug logging similar to SQLAlchemy echo
        should_echo = (echo is True) or (echo is None and settings.DEBUG)
        if should_echo:
            logging.getLogger("tortoise").setLevel(logging.DEBUG)

    @classmethod
    async def stop(cls) -> None:
        """
        Close all ORM connections.
        """
        if cls.started:
            await Tortoise.close_connections()
            cls.started = False


async def get_db() -> AsyncGenerator[BaseDBAsyncClient, None]:
    """
    FastAPI dependency that provides a transactional DB client.

    Usage:
        async def handler(db: BaseDBAsyncClient = Depends(get_db)):
            await Ticket.filter(...).using_db(db).update(...)
            # Transaction will commit on success or rollback on exception.

    NOTE:
    * Use `.using_db(db)` on queries to bind them to this transaction.
    * If you do not need a transaction, you can get a pooled client via `get_db_client()`.
    """
    async with in_transaction("default") as db:
        yield db


def get_db_client() -> BaseDBAsyncClient:
    """
    Return the pooled DB client (no transaction). Useful for read-only operations.
    """
    return connections.get("default")
