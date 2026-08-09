from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    reload: bool = True
    factory: bool = True


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 5
    pool_size: int = 10
    pool_pre_ping: bool = True


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    run: RunConfig = RunConfig()
    db: DatabaseConfig


settings = Settings()
