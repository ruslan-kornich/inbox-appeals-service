"""
Global pytest fixtures and helpers for the FastAPI + Tortoise project.

This module:
- Sets test-time environment variables (JWT and DB DSN).
- Initializes a dedicated SQLite database and generates schemas without Aerich.
- Creates an HTTPX AsyncClient with lifespan disabled (we control DB lifecycle).
- Provides helpers to create users of different roles and to mint JWT tokens.
"""
from __future__ import annotations

import asyncio
import importlib
import os
import sys
import types
from typing import AsyncIterator, Callable, Tuple

import pytest
from faker import Faker
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop() -> AsyncIterator[asyncio.AbstractEventLoop]:
    """
    Create an isolated event loop for the test session.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def _test_env(tmp_path_factory: pytest.TempPathFactory):
    """
    Configure environment variables for the whole test session:
    - Use a file-based SQLite database (shared across connections).
    - Provide JWT configuration (secret/algorithm/expiry).
    Then reload settings and DB config modules so they pick up env.
    """
    db_dir = tmp_path_factory.mktemp("db")
    db_path = db_dir / "test.db"
    os.environ["ASYNC_DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["JWT_ACCESS_EXPIRES_MINUTES"] = "60"
    os.environ.setdefault("DEBUG", "true")

    # Reload settings and db config to pick up the fresh env.
    import app.config.settings as settings_module
    import app.config.db as db_module

    importlib.reload(settings_module)
    importlib.reload(db_module)

@pytest.fixture(scope="session", autouse=True)
async def _init_tortoise(_test_env):
    """
    Initialize Tortoise ORM with the app's configuration and generate schemas.

    We do NOT run Aerich in tests. Schemas are generated on the fly.
    """
    from app.config.db import TORTOISE_ORM

    # Ensure "aerich.models" import won't fail if Aerich is not installed.
    try:
        importlib.import_module("aerich.models")
    except Exception:
        aerich_mod = types.ModuleType("aerich")
        aerich_models_mod = types.ModuleType("aerich.models")
        sys.modules.setdefault("aerich", aerich_mod)
        sys.modules.setdefault("aerich.models", aerich_models_mod)

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()

@pytest.fixture()
def app():
    """
    Provide a fresh FastAPI app instance.
    We will disable lifespan in the HTTPX transport to avoid reinitializing DB.
    """
    from app.main import create_app
    return create_app()

@pytest.fixture()
async def client(app) -> AsyncIterator[AsyncClient]:
    """
    Create an AsyncClient that talks to the ASGI app with lifespan disabled.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client

# --------------------------
# Factories / helper methods
# --------------------------

@pytest.fixture(scope="session")
def faker() -> Faker:
    """Provide a single Faker instance for the session."""
    return Faker("uk_UA")

async def _create_admin_user(email: str, password: str) -> Tuple[str, str]:
    """Create an ADMIN user directly via repository and return (user_id, token)."""
    from app.models import UserRole
    from app.repositories.users_repository import UserRepository
    from app.services.auth_service import hash_password
    from app.security.jwt import create_access_token

    repository = UserRepository()
    user = await repository.create(
        values={"email": email, "password_hash": hash_password(password), "role": UserRole.ADMIN}
    )
    token = create_access_token(subject=str(user.id), role=user.role.value)
    return str(user.id), token

async def _create_staff_user(email: str, password: str) -> Tuple[str, str]:
    """Create a STAFF user directly via repository and return (user_id, token)."""
    from app.models import UserRole
    from app.repositories.users_repository import UserRepository
    from app.services.auth_service import hash_password
    from app.security.jwt import create_access_token

    repository = UserRepository()
    user = await repository.create(
        values={"email": email, "password_hash": hash_password(password), "role": UserRole.STAFF}
    )
    token = create_access_token(subject=str(user.id), role=user.role.value)
    return str(user.id), token

async def _register_user_via_service(email: str, password: str) -> Tuple[str, str]:
    """
    Register a USER (with citizen profile) through the service and return (user_id, token).
    """
    from app.schemas.auth import RegisterUserBody
    from app.services.auth_service import AuthService
    from app.security.jwt import create_access_token

    service = AuthService()
    user_id, role = await service.register_user(
        RegisterUserBody(
            email=email,
            password=password,
            inn="1234567890",
            phone="+380501234567",
            first_name="Іван",
            last_name="Іванов",
            middle_name="Петрович",
            birth_date="1990-01-01",
        )
    )
    token = create_access_token(subject=user_id, role=role.value)
    return user_id, token

@pytest.fixture()
def make_admin_factory() -> Callable[[str, str], AsyncIterator[Tuple[str, str]]]:
    """Factory to create admin users inside tests."""

    async def _factory(email: str, password: str) -> Tuple[str, str]:
        return await _create_admin_user(email, password)

    return _factory

@pytest.fixture()
def make_staff_factory() -> Callable[[str, str], AsyncIterator[Tuple[str, str]]]:
    """Factory to create staff users inside tests."""

    async def _factory(email: str, password: str) -> Tuple[str, str]:
        return await _create_staff_user(email, password)

    return _factory

@pytest.fixture()
def register_user_factory() -> Callable[[str, str], AsyncIterator[Tuple[str, str]]]:
    """Factory to register regular users inside tests."""

    async def _factory(email: str, password: str) -> Tuple[str, str]:
        return await _register_user_via_service(email, password)

    return _factory

def auth_header(token: str) -> dict[str, str]:
    """Build Authorization header for bearer token."""
    return {"Authorization": f"Bearer {token}"}
