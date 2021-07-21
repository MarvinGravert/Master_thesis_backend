"""this modules coordinates all the information and communication necessary to find the correspondacne beetween lighthsoue
world and hololens world

it does so utliizing asnyc whereever necessary
"""
import asyncio
from typing import List
import copy

import numpy as np
from loguru import logger

# from backend_api.vr_objects import ViveTracker
from backend_api.exceptions import IncorrectMessageFormat
from backend_utils.averageQuaternion import averageQuaternions
from backend_utils.information_processor import InformationProcessor
from backend_api.grpc_objects import Pose

from config.const import (
    POINT_REGISTER_HOST, POINT_REGISTER_PORT, BACKEND_HOST, BACKEND_PORT,
    WAYPOINT_MANAGER_HOST, WAYPOINT_MANAGER_PORT
)
from modules.communication.grpc_client import PointRegisterCommunicator
from modules.point_correspondance.find_point_corresponder import get_points_tracker_kos, get_points_unity_kos
from utils.information_logger import DataLogger
from config.const import CALIBRATION_OBJECT

from config.api import Task


async def worker(queue: asyncio.Queue):
    # Start server
    logger.info("Worker has started")
    """
    ------------------
    SETTING UP THE IPs and the clients
    ------------------
    """

    points_register_host_ip = POINT_REGISTER_HOST
    points_register_host_port = POINT_REGISTER_PORT
    ####################

    points_register_client = PointRegisterCommunicator(
        points_register_host_ip, points_register_host_port)
    """
    ------------------
    Start the services
    ------------------
    """
    while True:
        datalog = DataLogger()  # init a new data logger for the new job
        task: Task = await queue.get()
        logger.info("New job has arrived. Start processing")
        tracker_poses, virtual_poses = await InformationProcessor().process_hololens_data(task.message)

        # find point correspondances=>match=>transformatoin has been found
        # 1. transform virutal posesto subsitute right handed KOS
        # 2. Create the transformation
        # 3. Send back

        """
        ------------------
        Get homogenous matrix
        ------------------
        """
        tracker_matrices = [pose.as_homogenous_matrix() for pose in tracker_poses]
        hololens_matrices = [pose.as_homogenous_matrix() for pose in virtual_poses]
        """     
        ------------------
        get the point correspondances
        ------------------
        """
        point_tracker_list = []
        for tracker_matrix in tracker_matrices:
            p = get_points_tracker_kos(tracker_matrix)
            point_tracker_list.extend(p)
        point_tracker_matrix = np.array(point_tracker_list)
        point_hololens_list = []
        for hololens_matrix in hololens_matrices:
            p = get_points_unity_kos(hololens_matrix)
            point_hololens_list.extend(p)
        point_hololens_matrix = np.array(point_hololens_list)
        """
        ------------------
        turn data to right handed kos
        ------------------
        turn z to -z
        """
        point_hololens_matrix[:, 2] = -point_hololens_matrix[:, 2]
        """
        ------------------
        calculate point registering
        ------------------
        """
        reprojection_error, hom_matrix_LH_to_virtual = await points_register_client.register_points(
            point_set_1=point_tracker_matrix[:, :3],
            point_set_2=point_hololens_matrix[:, :3]
        )
        logger.info(
            f"Transformtion-Matrix: LH to hololens world right handed:\n {hom_matrix_LH_to_virtual} ")
        # datalog.hom_LH_to_virtual = hom_matrix_LH_to_virtual
        """
        ------------------
        turn matrix back to left handed
        ------------------
        1. negate third row and third column=>(3,3) remains same
        2. turn to quaternion
        """
        hom_matrix_LH_to_virtual[2, :] = -hom_matrix_LH_to_virtual[2, :]
        hom_matrix_LH_to_virtual[:, 2] = -hom_matrix_LH_to_virtual[:, 2]
        logger.debug(hom_matrix_LH_to_virtual)
        # """
        # ------------------
        # Log data
        # ------------------
        # """
        # datalog.hololens_message = hololens_message
        # datalog.calibration_position = hologram_position
        # datalog.calibration_rotation = hologram_rotation
        # datalog.calibration_tracker = ViveTracker(
        #     rotation=tracker_state.calibration_tracker.rotation,
        #     position=tracker_state.calibration_tracker.position)
        # datalog.holo_tracker = ViveTracker(
        #     rotation=tracker_state.holo_tracker.rotation,
        #     position=tracker_state.holo_tracker.position)
        # datalog.reprojection_error = reprojection_error
        # datalog.real_points = real_cali_points
        # datalog.virtual_points = virtual_cali_points
        # datalog.calibration_object = str(CALIBRATION_OBJECT)
        # """
        # ------------------
        # Save the log containing the calibration to file
        # ------------------
        # """
        # logger.debug("Starting writing data log to file")
        # try:
        #     datalog.write_to_file()
        # except Exception as e:
        #     import traceback
        #     logger.error(e)
        #     logger.error(traceback.format_exc())
        # finally:
        #     # TODO: Save the config into a persistent memory
        #     queue.task_done()
        #     logger.info("Task done")
        task.callback_event.set()
        task.transformation = Pose(position=[0, 0, 0], rotation=[0, 0, 0, 1])
        queue.task_done()
        logger.info("Task done")
