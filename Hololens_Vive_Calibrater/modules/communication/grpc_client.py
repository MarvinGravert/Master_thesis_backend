"""This modules offers a client based grpc interface to communicate with the
backend servicer as well as the point registration module.

Depending on the what to use call the register_points or the interfacing with the backend servicer to get the tracker positon
"""
import asyncio
from typing import List, Tuple

import grpc
import grpc.aio
from loguru import logger
import numpy as np

from point_set_registration_pb2 import Input, Vector, RANSACParameters, Algorithm, Output
import holoViveCom_pb2_grpc
import point_set_registration_pb2_grpc

from backend_utils.object_pose_averager import average_vr_pose


class GRPCCommunicator():
    def __init__(self, server_address: str, server_port):
        self._server = server_address
        self._port = server_port


class PointRegisterCommunicator(GRPCCommunicator):
    async def register_points(self, point_set_1: np.ndarray, point_set_2: np.ndarray) -> Tuple[float, np.ndarray]:
        """Creates the GRPC Stub to communicate with the point registration service
        forwards the received parameters and returns the rotation R and translation t
        Transformation is from Set 1 to Set 2

        Args:
            point_set_1 (np.ndarray): nx3 set of points in Frame A
            point_set_2 (np.ndarray): nx3 set of points in Frame B
        Returns:
            (np.ndarray): R,t homogenouous matrix
        """
        logger.info("Start communication with server")
        """
        BUILD request
        """
        algorithm: Algorithm = Algorithm(type=Algorithm.Type.ARUN,
                                         ransac=RANSACParameters(
                                             threshold=3, confidence=0.95))
        point_set_1 = [Vector(entries=x) for x in point_set_1]
        point_set_2 = [Vector(entries=x) for x in point_set_2]
        obj_to_send = Input(
            algorithm=algorithm,
            pointSet_1=point_set_1,
            pointSet_2=point_set_2,
        )
        """
        Send Request and Wait Answer
        """
        async with grpc.aio.insecure_channel(f"{self._server}:{self._port}") as channel:
            logger.info(
                f"Started {self.__class__.__name__} communicator on {self._server}:{self._port}")
            stub = point_set_registration_pb2_grpc.PointSetRegisteringStub(channel=channel)

            response = await stub.registerPointSet(obj_to_send, timeout=10)
        return self.process_response(response)

    def process_response(self, async_response: Output) -> Tuple[float, np.ndarray]:
        logger.debug(f"server response: {async_response}")
        hom_matrix = np.reshape(async_response.transformationMatrixRowMajor, (4, 4))
        return async_response.reprojectionError, hom_matrix
