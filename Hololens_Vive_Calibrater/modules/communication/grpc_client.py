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

from holoViveCom_pb2 import Status, LighthouseState, CalibrationInfo, InformationRequest
from point_set_registration_pb2 import Input, Vector, RANSACParameters, Algorithm, Output
import holoViveCom_pb2_grpc
import point_set_registration_pb2_grpc
from backend_api.vr_objects import (
    ViveTracker, ViveController
)
from backend_utils.object_pose_averager import average_vr_pose

from config.const import NUM_LIGHTHOUSE_SAMPLES
from config.api import VRState


class GRPCCommunicator():
    def __init__(self, server_address: str, server_port):
        self._server = server_address
        self._port = server_port

    async def update_calibration_info(self, calibration: np.ndarray) -> None:
        """sends the calibration thats was selected by the hololens user OR when a new calibration has been calculated
        """
        logger.info("Starting process to update service about the new calibration")
        async with grpc.aio.insecure_channel(f"{self._server}:{self._port}") as channel:
            logger.info(
                f"Started {self.__class__.__name__} communicator on {self._server}:{self._port}")
            stub = holoViveCom_pb2_grpc.BackendStub(channel=channel)
            await stub.UpdateCalibrationInfo(CalibrationInfo(calibrationMatrixRowMajor=calibration.flatten()))
        logger.debug("Message has been sent")


class WayPointManagerCommunicator(GRPCCommunicator):
    pass


class BackendCommunicator(GRPCCommunicator):
    """
        ---------------------
        ProvideLighthouseState
        ---------------------
    """
    async def get_tracker_pose(self) -> VRState:
        """Sends an empty status to the backend server and receives back the position of the both the trackers
        The returned trackerstate object is then used to create the vr_state
        """
        logger.info("Start communication wiht server")
        async with grpc.aio.insecure_channel(f"{self._server}:{self._port}") as channel:
            logger.info(
                f"Started {self.__class__.__name__} communicator on {self._server}:{self._port}")
            stub = holoViveCom_pb2_grpc.BackendStub(channel=channel)
            list_holo_tracker = list()
            list_calibration_tracker = list()
            async for async_response in stub.ProvideLighthouseState(
                    InformationRequest(numberSamples=NUM_LIGHTHOUSE_SAMPLES)):
                holo_tracker, cali_tracker = await self.process_response(async_response=async_response)
                list_holo_tracker.append(holo_tracker)
                list_calibration_tracker.append(cali_tracker)
                logger.debug(cali_tracker)

            """
            Process reponse and return
            """

            logger.info("Received Tracker Data. Starting Parsing and averaging it")
            holo_tracker: ViveTracker = average_vr_pose(list_vr_object=list_holo_tracker)
            cali_tracker: ViveTracker = average_vr_pose(list_vr_object=list_calibration_tracker)

        # 10,10,10,0,0,1,0end
        return await self.build_vr_state(holo_tracker=holo_tracker, cali_tracker=cali_tracker)

    async def process_response(self, async_response: LighthouseState) -> Tuple[ViveTracker, ViveTracker]:
        logger.debug(f"server response: {async_response}")
        holo_tracker = ViveTracker.set_pose_via_grpc_object(async_response.holoTracker)
        cali_tracker = ViveTracker.set_pose_via_grpc_object(async_response.caliTracker)
        return holo_tracker, cali_tracker

    async def build_vr_state(self, holo_tracker: ViveTracker, cali_tracker: ViveTracker) -> VRState:
        vr_state = VRState()
        vr_state.holo_tracker = holo_tracker
        vr_state.calibration_tracker = cali_tracker
        return vr_state


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
