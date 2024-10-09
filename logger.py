import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name, log_to_file=False):
    log_path = os.path.join(os.path.expanduser("~"), 'mysite', 'logs')
    os.makedirs(log_path, exist_ok=True)

    if log_to_file:
        handler = RotatingFileHandler(os.path.join(log_path, 'app.log'), maxBytes=10000000, backupCount=3, encoding='utf-8')
    else:
        handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)

    return logger
