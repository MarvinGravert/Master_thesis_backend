from concurrent import futures

import grpc
from loguru import logger

import point_set_registration_pb2
import point_set_registration_pb2_grpc

from config.config import GRPC_PORT, RUNTIME_HOST, MAX_WORKERS
from modules.base_server import PointSetRegistering


def serve():
    server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    point_set_registration_pb2_grpc.add_PointSetRegisteringServicer_to_server(
        servicer=PointSetRegistering(), server=server)
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    server.start()
    server.wait_for_termination()


class Server:
    def serve(self):
        logger.info(
            f"Server started on Address: [::], Port: {GRPC_PORT}")
        serve()


if __name__ == "__main__":
    Server().serve()
