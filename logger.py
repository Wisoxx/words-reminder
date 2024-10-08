import logging
from logging.handlers import RotatingFileHandler
import os

log_path = os.path.join(os.path.expanduser("~"), 'mysite', 'logs')
os.makedirs(log_path, exist_ok=True)

handler = RotatingFileHandler(os.path.join(log_path, 'app.log'), maxBytes=10000000, backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
                              datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

# Set up the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # Set the logging level for all loggers
root_logger.addHandler(handler)

# logging.basicConfig(
#     filename='logs.log',
#     filemode='a',
#     level=logging.DEBUG,
#     format='%(asctime)s:%(levelname)s:%(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
# )