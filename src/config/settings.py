from pathlib import Path


class BaseAppSettings:
    BASE_DIR: Path = Path(__file__).parent.parent


class Settings(BaseAppSettings):
    POSTGRES_DB: str = "test_db"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    POSTGRES_HOST: str = "test_host"
    POSTGRES_PORT: int = "port"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
