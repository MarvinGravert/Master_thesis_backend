from types import new_class
import grpc

from loguru import logger

from holoViveCom_pb2 import Status
import holoViveCom_pb2_grpc

from config.const import (
    BACKEND_SERVICER_IP, BACKEND_SERVICER_PORT
)


def run(status: str):
    logger.info("starting communication with backend server")
    with grpc.insecure_channel(f"{BACKEND_SERVICER_IP}:{BACKEND_SERVICER_PORT}") as channel:
        stub = holoViveCom_pb2_grpc.BackendStub(channel=channel)

        stub.ChangeStatus(Status(status=status))
    logger.info("Send new status to server")


if __name__ == "__main__":
    new_status = "test"
    run(status=new_status)
