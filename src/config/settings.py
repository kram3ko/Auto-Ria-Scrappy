import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT"))


def get_settings() -> Settings:
    """
    Creates and caches a Settings instance.
    The lru_cache ensures this is only done once.
    """
    return Settings()
