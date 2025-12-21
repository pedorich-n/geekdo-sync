from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    geekdo: GeekdoConfig
    grist: GristConfig
