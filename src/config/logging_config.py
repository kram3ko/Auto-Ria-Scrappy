import logging
from src.config.settings import get_settings

def setup_logging_from_settings():
    cfg = get_settings()
    log_level = getattr(logging, cfg.LOG_LEVEL.upper(), logging.INFO)
    log_kwargs = {
        'level': log_level,
        'format': cfg.LOG_FORMAT,
    }
    if cfg.LOG_FILE:
        log_kwargs['filename'] = cfg.LOG_FILE
    logging.basicConfig(**log_kwargs) 