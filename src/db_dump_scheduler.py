import os
from datetime import datetime
from pathlib import Path
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from src.config.settings import get_settings
from src.config.logging_config import setup_logging_from_settings

def dump_db():
    cfg = get_settings()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dump_dir = Path("dumps")
    dump_dir.mkdir(exist_ok=True)
    dump_path = dump_dir / f"dump_{timestamp}.sql"
    cmd = (
        f'pg_dump -U {cfg.POSTGRES_USER} '
        f'-h {cfg.POSTGRES_HOST} '
        f'-p {cfg.POSTGRES_PORT} '
        f'-d {cfg.POSTGRES_DB} > "{dump_path}"'
    )
    logging.info(f"Executing dump command: {cmd}")
    env = os.environ.copy()
    if cfg.POSTGRES_PASSWORD:
        env['PGPASSWORD'] = cfg.POSTGRES_PASSWORD
    result = os.system(cmd)
    if result == 0:
        logging.info(f"Dump created successfully: {dump_path}")
    else:
        logging.error(f"Dump creation failed. Return code: {result}. Check connection parameters and 'pg_dump' availability.")

if __name__ == "__main__":
    setup_logging_from_settings()
    settings = get_settings()
    dump_time = settings.DUMP_TIME
    timezone = settings.DUMP_TIMEZONE
    try:
        hour, minute = map(int, dump_time.split(":"))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError("Invalid time specified.")
    except ValueError as e:
        logging.error(f"Error in dump time format ('{dump_time}'). Use 'HH:MM' format. Error: {e}")
        exit(1)
    scheduler = BlockingScheduler(timezone=timezone)
    scheduler.add_job(dump_db, 'cron', hour=hour, minute=minute)
    logging.info(f"Scheduler started. Dump will run daily at {dump_time} ({timezone}).")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")
