
"""this modules coordinates all the information and communication necessary to find the correspondacne beetween lighthsoue
world and hololens world

it does so utliizing asnyc whereever necessary
"""
import asyncio
from typing import List, Union
from backend_api.general import InterpolationType, Waypoint

import numpy as np
from loguru import logger
from scipy.spatial.transform import Rotation as R

from backend_utils.information_processor import InformationProcessor
from backend_utils.averageQuaternion import averageQuaternions
from backend_utils.linear_algebra_helper import separate_from_homogeneous_matrix

from config.api_types import ServerState
from backend_api.exceptions import IncorrectMessageFormat


class WorkerClass():
    def __init__(self) -> None:
        self.information_processor = InformationProcessor()

    async def worker(self, queue: asyncio.Queue, server_state: ServerState):
        # Start server
        logger.info("Worker has started")
        self.server_state = server_state
        """
        ------------------
        Start the services
        ------------------
        """
        while True:
            hololens_message: List[str] = await queue.get()
            logger.info("New path has arrived. Start processing")
            # first we can get the data from the trackers
            """
                ------------------
               PATH processing
                ------------------
            """
            try:

                # Path
                path: List[Waypoint] = await self.information_processor.process_path_information(hololens_message)

            except IncorrectMessageFormat:
                logger.error("Message has the incorrect format. Dicarding job")
                queue.task_done()
                continue
            for waypoint in path:
                waypoint.apply_offset(np.array([0, -0.0145, 0.1735]))  # offset in m!
            logger.info(f"The path is:\n {path}")

            """
            ------------------
            Transform all waypoints into robot workspace
            ------------------
            The received waypoints are the ones taken in the vive lighthouse 
            and not transformed thus no correction for lefthanded or righthanded has to be applied 
            """

            hom_matrix = self.server_state.hom_matrix_LH_Robo
            logger.info("KUKA waypoints")
            for waypoint in path:
                # point_in_robo = hom_matrix@np.append(waypoint.position, 1)
                # logger.info(f"{waypoint.type}: {point_in_robo[:3]}")
                position, angles = self.get_pos_rot_in_kuka_kos(waypoint, lh2robot=hom_matrix)
                logger.info(f"{waypoint.type}: XYZ: {position} ABC: {angles}")

            avg_waypoint = self.average_waypoints(path)
            avg_pos, avg_angle = self.get_pos_rot_in_kuka_kos(avg_waypoint, lh2robot=hom_matrix)
            logger.info("AVERAGE")
            logger.info(f"avgPos: {avg_pos}  avgAngles (ABC): {avg_angle}")

    def get_pos_rot_in_kuka_kos(self, waypoint: Waypoint, lh2robot):

        cont2lh = waypoint.as_hom_matrix()
        cont2robot = lh2robot@cont2lh
        rot, t = separate_from_homogeneous_matrix(cont2robot)
        # rot is the controller->base but we need base->controller as controller should be
        # waypoint
        rot_base_waypoint = np.linalg.inv(rot)
        euler = R.from_matrix(rot_base_waypoint)
        angles = euler.as_euler('zyx', degrees=True)
        return t, angles

    def average_waypoints(self, waypoint_list: List[Waypoint]) -> Waypoint:

        pos_list = list()
        quat_list = list()
        for i in waypoint_list:
            pos_list.append(i.position)
            quat_list.append(i.rotation)

        avg_position = np.mean(np.array(pos_list), 0)
        quat_matrix = np.array(quat_list)
        # change w to first aka 0->1 1->2 etc. 3->0
        quat_matrix = quat_matrix[:, [3, 0, 1, 2]]

        avg_quat = averageQuaternions(quat_matrix)
        w, i, j, k = avg_quat
        return Waypoint(
            position=avg_position,
            rotation=np.array([i, j, k, w]),
            type=InterpolationType.Linear)
