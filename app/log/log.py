import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    "[%(asctime)s]-[%(levelname)s-%(filename)s:%(lineno)s]-> %(message)s"
)
filename = "./app/log/logs.log"
fileHandler = logging.FileHandler(filename)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

fileMaxBytes = 1024 * 1024 * 100
fileHandler = RotatingFileHandler(filename, maxBytes=fileMaxBytes, backupCount=100)
