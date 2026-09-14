import logging
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT
    date_format: str = "%Y-%m-%d %H:%M:%S"

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]


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


class BrokerConfig(BaseModel):
    url: str
    notification_topic_name: str
    dead_letter_topic_name: str
    poll_interval: int
    group_id: str
    auto_offset_reset: str  # с какого места консумер начнёт читать сообщения если нет сохранённого offset
    enable_auto_commit: bool
    max_poll_records: int  # количество сообщений, которое консумер получает за один poll
    acks: str
    enable_idempotence: bool
    linger_ms: int
    max_batch_size: int


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    logging: LoggingConfig = LoggingConfig()
    run: RunConfig = RunConfig()
    db: DatabaseConfig
    broker: BrokerConfig


settings = Settings()
