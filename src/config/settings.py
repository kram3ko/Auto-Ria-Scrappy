import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT"))
    DUMP_TIME: str = os.getenv("DUMP_TIME", "12:00")
    DUMP_TIMEZONE: str = os.getenv("DUMP_TIMEZONE", "Europe/Kiev")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str | None = os.getenv("LOG_FILE")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "[%(asctime)s] %(levelname)s: %(message)s")


def get_settings() -> Settings:
    """
    Creates and caches a Settings instance.
    The lru_cache ensures this is only done once.
    """
    return Settings()
