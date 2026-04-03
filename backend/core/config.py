from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Finance Dashboard Backend"

    # JWT
    ACCESS_TOKEN_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(
        default="HS256",
        validation_alias=AliasChoices("JWT_ALGORITHM", "ALGORITHM"),
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./finance.db",
        description="Database connection string",
    )

    # Rate Limiting
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    # ADMIN CONFIG (NOW ENV-DRIVEN)
    ADMIN_NAME: str = Field(..., description="Admin name")
    ADMIN_EMAIL: str = Field(..., description="Admin email")
    ADMIN_PASSWORD: str = Field(..., description="Admin password")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unknown env vars
    )


# singleton instance
settings = Settings()