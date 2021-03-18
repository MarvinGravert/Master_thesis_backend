import grpc

from loguru import logger

import holoViveCom_pb2_grpc
from holoViveCom_pb2 import (
    HandheldController, LighthouseState, InformationRequest
)
from config.consts import (
    BACKEND_HOST, BACKEND_PORT, NUM_LIGHTHOUSE_SAMPLES
)


def get_samples():

    logger.info("Starting Connection to backend Server")
    async with grpc.aio.insecure_channel(f"{BACKEND_HOST}:{BACKEND_PORT}") as channel:
        logger.info(
            f"Started communicator")
        stub = holoViveCom_pb2_grpc.BackendStub(channel=channel)
        res = list()
        for part in stub.ProvideLighthouseState(InformationRequest(
            numberSamples=NUM_LIGHTHOUSE_SAMPLES
        )):
            res.append(part)

        logger.debug(f"Received {len(res)} messages")

    return True


def process_into_matrix():
    l


if __name__ == "__main__":
    logger.info("Starting manual point gathering")
    get_samples()
