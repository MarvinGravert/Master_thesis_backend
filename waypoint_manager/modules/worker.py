
"""this modules coordinates all the information and communication necessary to find the correspondacne beetween lighthsoue
world and hololens world

it does so utliizing asnyc whereever necessary
"""
import asyncio
from typing import List, Union

import numpy as np
from loguru import logger
from scipy.spatial.transform import Rotation as R


from backend_utils.information_processor import InformationProcessor
from backend_api.vr_objects import VRObject

from config.const import (
    BACKEND_HOST, BACKEND_PORT
)
from modules.grpc_client import BackendCommunicator
from config.api_types import IncorrectMessageFormat, ServerState


class WorkerClass():
    def __init__(self) -> None:
        self.information_processor = InformationProcessor()

    async def worker(self, queue: asyncio.Queue, server_state: ServerState):
        # Start server
        logger.info("Worker has started")
        self.server_state = server_state
        backend_client = BackendCommunicator(server_address=BACKEND_HOST, server_port=BACKEND_PORT)
        """
        ------------------
        Start the services
        ------------------
        """
        while True:
            task: Union[VRObject, List[str]] = await queue.get()
            logger.info("New job has arrived. Start processing")
            # first we can get the data from the trackers
            tracker_state = await backend_client.get_tracker_pose()
            logger.debug("received information from trackers, now process information")
            """
                ------------------
                Check which workflow to use.
                Either treat task as a hololens waypoint or a waypoint set directly via controller
                ------------------
            """
            try:
                if isinstance(task, list):
                    logger.debug("waypoint is from hololens=>starting hololens workflow")
                    waypoint = await self.workflow_hololens_waypoint(hololens_message=task,
                                                                     tracker_state=tracker_state)
                elif isinstance(task, VRObject):
                    logger.debug(
                        "waypoint is directly set via the controller->Starting the controller workflow")
                    waypoint = await self.workflow_controller_waypoint(controller=task)
                else:
                    logger.error("waypoint didnt fit any workflow")
                    queue.task_done()
                    continue
            except IncorrectMessageFormat:
                logger.error("Message has the incorrect format. Dicarding job")
                queue.task_done()
                continue

            logger.info(f"The waypoint is:\n {waypoint}")

    async def workflow_controller_waypoint(self,
                                           controller: VRObject,
                                           ) -> np.ndarray:
        logger.debug("start controller waypoint workflow")
        """
        ------------------
        get vr object homogenous matrix
        ------------------
        """
        hom_matrix_controller_2_LH = controller.get_pose_as_hom_matrix()
        waypointmarker = np.array([0, -0.012, 0.173, 1])  # NOTE: adjusted to unity values
        print(hom_matrix_controller_2_LH)
        print(self.server_state.LH2Robo.matrix)
        """
        ------------------
        calculate desired transformation
        ------------------
        """
        LH_2_robot_matrix = self.server_state.LH2Robo.matrix

        return (LH_2_robot_matrix@hom_matrix_controller_2_LH@waypointmarker.reshape((-1, 1)))[:3]

    async def workflow_hololens_waypoint(self, hololens_message: List[str],
                                         tracker_state: ServerState) -> np.ndarray:
        logger.debug("start hololens workflow")
        hologram_position, hologram_rotation = await self.information_processor.process_hololens_data(hololens_message)

        """
        ------------------
        get tracker transformation
        ------------------
        """
        holo_tracker_hom_matrix = tracker_state.holo_tracker.get_pose_as_hom_matrix()
        """
        ------------------
        calculate desired transformation
        ------------------
        """
        hom_hologram_2_virtual_center = self._transform_unity_quat_into_hom(
            unity_position=hologram_position,
            unity_quaternion=hologram_rotation)
        LH_2_robot_matrix = self.server_state.LH2Robo.matrix
        LH_2_virtual_center = self.server_state.LH2Virtual.matrix
        # TODO: include the tracker instead of the direct transform
        hologram_2_robo = LH_2_robot_matrix@np.linalg.inv(
            LH_2_virtual_center)@hom_hologram_2_virtual_center
        return hologram_2_robo

    def _transform_unity_quat_into_hom(
            self,
            unity_position: List[float],
            unity_quaternion: List[float]) -> np.ndarray:
        """turns the left handed KOS pose (postion+quaternion) into a right handed
        homogenous matrix

        Args:
            unity_position (List[float]): x y z in unity KOS (aka lefthanded)
            unity_quaternion (List[float]): i j k w in unity KOS (aka lefthanded)

        Returns:
            np.ndarray: 4x4 righthanded hom matrix
        """
        x, y, z = unity_position
        i, j, k, w = unity_quaternion
        rotation_matrix = R.from_quat([-i, -k, -j, w]).as_matrix()
        position_vector = np.array([x, z, y])
        hom_matrix = np.hstack((rotation_matrix, position_vector.reshape((-1, 1))))
        return np.vstack((hom_matrix, [0, 0, 0, 1]))
