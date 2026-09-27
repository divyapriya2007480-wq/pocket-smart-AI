from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "divya-super-secret-key-12345-pocketsmart"
    database_url: str = "sqlite:///./pocketsmart.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    allowed_hosts: str = "*"
    cors_origins: str = "*"
    session_max_age_seconds: int = 3600

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def allowed_host_list(self) -> list[str]:
        return [v.strip() for v in self.allowed_hosts.split(",") if v.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [v.strip() for v in self.cors_origins.split(",") if v.strip()]

settings = Settings()