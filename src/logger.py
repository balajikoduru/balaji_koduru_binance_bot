import logging
from logging.handlers import RotatingFileHandler

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

def get_logger(name: str = "bot") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fh = RotatingFileHandler("bot.log", maxBytes=2_000_000, backupCount=3)
    fh.setFormatter(logging.Formatter(_LOG_FORMAT))
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(_LOG_FORMAT))
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
