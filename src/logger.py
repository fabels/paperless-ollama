import logging

from config import Config

def setup_logging():
    logging.basicConfig(level=Config.LOG_LEVEL)