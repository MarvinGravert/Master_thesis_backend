"""This modules offers a client based grpc interface to communicate with the
backend servicer as well as the point registration module.

Depending on the what to use call the register_points or the interfacing with the backend servicer to get the tracker positon
"""
from typing import List

import grpc
import grpc.aio
from loguru import logger
import numpy as np

from holoViveCom_pb2 import Status, TrackerState, CalibrationInfo
from point_set_registration_pb2 import Input, Vector, RANSACParameters, Algorithm, Output

import holoViveCom_pb2_grpc
import point_set_registration_pb2_grpc

from config.api_types import VRState


class GRPCCommunicator():
    def __init__(self, server_address: str, server_port):
        self._server = server_address
        self._port = server_port


class BackendCommunicator(GRPCCommunicator):
    async def get_tracker_pose(self) -> VRState:
        """Sends an empty status to the backend server and receives back the position of the both the trackers
        The returned trackerstate object is then used to create the vr_state
        """
        logger.info("Star communication wiht server")

        async with grpc.aio.insecure_channel(f"{self._server}:{self._port}") as channel:
            logger.info(
                f"Started {self.__class__.__name__} communicator on {self._server}:{self._port}")
            stub = holoViveCom_pb2_grpc.BackendStub(channel=channel)
            response = await stub.ProvideTrackerInfo([])
        """
        Process reponse and return
        """
        logger.info("Received Tracker Data. Starting Parsing it")
        # 10,10,10,0,0,1,0end
        return self.process_response(async_response=response)

    def process_response(self, async_response: TrackerState) -> VRState:
        logger.debug(f"server response: {async_response}")
        vr_state = VRState()
        vr_state.init_calibration_tracker(async_response.caliTracker)
        vr_state.init_holo_tracker(async_response.holoTracker)
        return vr_state

    async def update_calibration_info(self, calibration: np.ndarray) -> None:
        """sends the calibration thats was selected by the hololens user OR when a new calibration has been calculated
        """
        logger.info("Starting process to update backend service about the new calibration")
        async with grpc.aio.insecure_channel(f"{self._server}:{self._port}") as channel:
            logger.info(
                f"Started {self.__class__.__name__} communicator on {self._server}:{self._port}")
            stub = holoViveCom_pb2_grpc.BackendStub(channel=channel)
            await stub.UpdateCalibrationInfo(CalibrationInfo(calibrationMatrixRowMajor=calibration.flatten()))
        logger.debug("Message has been sent")


class PointRegisterCommunicator(GRPCCommunicator):
    async def register_points(self, point_set_1: np.ndarray, point_set_2: np.ndarray) -> np.ndarray:
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
        algorithm: Algorithm = Algorithm(type=Algorithm.Type.OPENCV,
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

    def process_response(self, async_response: Output) -> np.ndarray:
        logger.debug(f"server response: {async_response}")
        R = list()
        t = list()
        for row, entry in zip(async_response.rotationMatrix,
                              async_response.translationVector.entries):
            R.append(row.row)
            t.append(entry)
        R = np.array(R)
        t = np.array(t).reshape([3, 1])
        hom_matrix = np.hstack([R, t])
        hom_matrix = np.vstack([hom_matrix, [0, 0, 0, 1]])
        reprojection_error = float(Output.status)
        return reprojection_error, hom_matrix
