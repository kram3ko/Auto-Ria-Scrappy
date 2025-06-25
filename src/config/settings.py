from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SettingsConfigDict(env_file=".env")
    BASE_DIR: Path = Path(__file__).parent.parent
    POSTGRES_DB: str = "test_db"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    POSTGRES_HOST: str = "test_host"
    POSTGRES_PORT: int = 5432

    model_config = SettingsConfigDict(env_file=".env")



def get_settings() -> Settings:
    return Settings()
