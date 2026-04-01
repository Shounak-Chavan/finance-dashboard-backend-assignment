from pydantic_settings import BaseSettings
from pydantic import AliasChoices, Field


class Settings(BaseSettings):
    # 🔥 App
    APP_NAME: str = "Finance Dashboard Backend"

    # 🔐 JWT
    ACCESS_TOKEN_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(
        default="HS256",
        validation_alias=AliasChoices("JWT_ALGORITHM", "ALGORITHM"),
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # 🗄️ Database
    DATABASE_URL: str = Field(..., description="Database connection string")

    # 🚦 Rate Limiting
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ⚙️ Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 🔥 singleton instance
settings = Settings()