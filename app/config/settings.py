import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Service wide settings.
    """

    SERVICE_NAME: str = Field("Appeals", frozen=True)
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    BACKEND_URL: str | None = "http://127.0.0.1:8000"
    FRONTEND_URL: str | None = None

    ASYNC_DATABASE_URL: str  = "postgresql+asyncpg://inbox:Strong123@localhost:5432/inbox_appeals"



    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def __init__(self, **kwargs: dict[str, str]) -> None:
        """
        Init variables using AWS credentials.
        """
        super().__init__(**kwargs)



settings = Settings()
