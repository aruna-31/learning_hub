import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Application configurations loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    ALGORITHM: str = Field("HS256", validation_alias="ALGORITHM")
    FRONTEND_ORIGINS: str = Field(
        "http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="FRONTEND_ORIGINS"
    )
    YOUTUBE_API_KEY: str = Field("", validation_alias="YOUTUBE_API_KEY")
    GITHUB_TOKEN: str = Field("", validation_alias="GITHUB_TOKEN")

settings = Settings()
