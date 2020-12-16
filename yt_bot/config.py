from loguru import logger
from os import getenv
from sys import stderr
from sqlalchemy.ext.declarative import declarative_base
import pretty_errors

Base = declarative_base()
logger.remove()
logger.add(
    stderr,
    level=getenv('LOG_LEVEL') or 'DEBUG',
    diagnose=False,
    backtrace=False)
pretty_errors.configure(display_link=True)
