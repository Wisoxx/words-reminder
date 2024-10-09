import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name):
    log_path = os.path.join(os.path.expanduser("~"), 'mysite', 'logs')
    os.makedirs(log_path, exist_ok=True)

    file_handler = RotatingFileHandler(os.path.join(log_path, 'app.log'), maxBytes=1000000, backupCount=4)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    console_handler.setFormatter(console_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
