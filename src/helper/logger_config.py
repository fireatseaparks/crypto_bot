import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from pythonjsonlogger import jsonlogger


def setup_logger():
    log_dir = Path("logs")
    
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
    
    logger = logging.getLogger("load data")
    logger.setLevel(logging.INFO)

    log_handler = RotatingFileHandler(log_dir / "crypto_bot.log", maxBytes=1_000_000, backupCount=3)
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    log_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(log_handler)

    return logger
