import logging
from enum import Enum, IntEnum

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogFormat(str, Enum):
    FULL = "full"  # Timestamp, level, message (for standalone execution)
    SYSTEMD = "systemd"  # Level and message only (systemd adds timestamps)
    SIMPLE = "simple"  # Message only (minimal output)


class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def _missing_(cls, value: object) -> "LogLevel | None":
        """Allow creation from string names (case-insensitive)."""
        if isinstance(value, str):
            try:
                return cls[value.upper()]
            except KeyError:
                pass
        return None


class LoggingConfig(BaseSettings):
    level: LogLevel = LogLevel.DEBUG
    format: LogFormat = LogFormat.FULL


class GeekdoConfig(BaseSettings):
    token: SecretStr
    username: str


class GristConfig(BaseSettings):
    # The rest of the fields are loaded by pygrister from the environment
    # See https://pygrister.readthedocs.io/en/latest/conf.html#configuration-keys
    model_config = SettingsConfigDict(extra="ignore")

    doc_id: str


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="_", env_nested_max_split=1)

    logging: LoggingConfig = LoggingConfig()
    geekdo: GeekdoConfig
    grist: GristConfig
