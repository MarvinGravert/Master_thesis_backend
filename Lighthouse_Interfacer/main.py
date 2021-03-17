import sys

from loguru import logger

from modules.grpc_interface import ForwardLighthouseData
from config.api_types import (
    StartupError
)

if __name__ == "__main__":
    logger.info("Starting Lighthouse Interfacer")
    logger.remove()
    logger.add(sink=sys.stderr,level="ERROR")
    try:
        grpc_interface = ForwardLighthouseData()
    except StartupError as e:
        logger.error("Startup went went wrong. Shutting Down")
        sys.exit()
    grpc_interface.connect()
