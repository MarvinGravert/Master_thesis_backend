from loguru import logger

from modules.grpc_interface import ForwardLighthouseData

if __name__ == "__main__":
    logger.info("Starting Lighthouse Interfacer")
    grpc_interface = ForwardLighthouseData()
    grpc_interface.connect()
