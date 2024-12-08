import sys
from loguru import logger as __logger
from loguru._defaults import LOGURU_FORMAT

# Remove the source location from the log output
__LOG_FORMAT = LOGURU_FORMAT.replace(
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - ", ""
)

__logger.remove()
__logger.add(
    sys.stderr,
    format=__LOG_FORMAT,
)
logger = __logger
