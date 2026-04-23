from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "OMC Leads API"
    app_version: str = "0.1.0"

    database_url: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    db_host: str | None = None
    db_port: int | None = None
    db_name: str | None = None

    db_auto_create: bool = True

    cors_allow_origins: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_headers: list[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if self.database_url:
            return self

        required_parts = [
            self.db_user,
            self.db_password,
            self.db_host,
            self.db_port,
            self.db_name,
        ]

        if all(part is not None for part in required_parts):
            self.database_url = (
                f"postgresql+psycopg://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
            return self

        raise ValueError(
            "Configura DATABASE_URL o todas las variables DB_USER, "
            "DB_PASSWORD, DB_HOST, DB_PORT y DB_NAME."
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
