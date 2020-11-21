from loguru import logger
from os import getenv
from sys import stderr
import pretty_errors

logger.remove()
logger.add(
    stderr,
    level=getenv('LOG_LEVEL') or 'DEBUG',
    diagnose=False,
    backtrace=False)
pretty_errors.configure(display_link=True)
