"""this modules coordinates all the information and communication necessary to find the correspondacne beetween lighthsoue
world and hololens world

it does so utliizing asnyc whereever necessary
"""
import asyncio
from typing import List, Tuple

import numpy as np
from loguru import logger

from config.const import (
    POINT_REGISTER_HOST, POINT_REGISTER_PORT, BACKEND_HOST, BACKEND_PORT,
    WAYPOINT_MANAGER_HOST, WAYPOINT_MANAGER_PORT
)
from modules.communication.grpc_client import BackendCommunicator, PointRegisterCommunicator, WayPointManagerCommunicator
from modules.point_correspondance.find_point_corresponder import get_points_real_object, get_points_virtual_object
from config.api_types import IncorrectMessageFormat, ViveTracker
from utils.information_logger import DataLogger
from config.const import CALIBRATION_OBJECT
from utils.averageQuaternion import averageQuaternions


async def worker(queue: asyncio.Queue):
    # Start server
    logger.info("Worker has started")
    """
    ------------------
    SETTING UP THE IPs and the clients
    ------------------
    """

    backend_host_ip = BACKEND_HOST
    backend_host_port = BACKEND_PORT
    points_register_host_ip = POINT_REGISTER_HOST
    points_register_host_port = POINT_REGISTER_PORT
    ####################
    backend_client = BackendCommunicator(backend_host_ip, backend_host_port)
    points_register_client = PointRegisterCommunicator(
        points_register_host_ip, points_register_host_port)
    waypoint_manager_client = WayPointManagerCommunicator(server_address=WAYPOINT_MANAGER_HOST,
                                                          server_port=WAYPOINT_MANAGER_PORT)
    """
    ------------------
    Start the services
    ------------------
    """
    while True:
        datalog = DataLogger()  # init a new data logger for the new job
        hololens_message: List[str] = await queue.get()
        logger.info("New job has arrived. Start processing")
        # now we can get the data from the trackers
        tracker_state = await backend_client.get_tracker_pose()
        # now  we can process the response we received from the hololens
        logger.debug("received information from trackers, now process information")
        """
        ------------------
        work through the messages
        ------------------
        """
        info_processor = InformationProcessor()
        try:
            hologram_position, hologram_rotation = await info_processor.process_hololens_data(hololens_message)

        except IncorrectMessageFormat:
            logger.error("Message has the incorrect format. Dicarding job")
            queue.task_done()
            continue

        """
        ------------------
        get the point correspondances
        ------------------
        """
        virtual_cali_points = get_points_virtual_object(
            unity_trans=hologram_position, unity_rot=hologram_rotation)
        real_cali_points = get_points_real_object(
            vive_trans=tracker_state.calibration_tracker.loc_trans,
            vive_rot=tracker_state.calibration_tracker.loc_rot
        )
        """
        ------------------
        calculate point registering
        ------------------
        """
        reprojection_error, hom_matrix_LH_to_virtual = await points_register_client.register_points(
            point_set_1=real_cali_points,
            point_set_2=virtual_cali_points
        )
        logger.info(f"Transformtion-Matrix: LH to virtual center:\n {hom_matrix_LH_to_virtual} ")
        datalog.hom_LH_to_virtual = hom_matrix_LH_to_virtual
        """
        ------------------
        get tracker transformation
        ------------------
        """
        tracker_hom_matrix = tracker_state.holo_tracker.get_as_hom_matrix()
        """
        ------------------
        calculate desired transformation
        ------------------
        """
        # now e can get the transformatoin from the tracker to the virtual center
        target_hom_matrix = hom_matrix_LH_to_virtual@tracker_hom_matrix
        logger.info(
            f"The transformation matrix:  tracker to virtual is:\n {target_hom_matrix}")
        datalog.hom_tracker_to_virtual = target_hom_matrix
        """
        ------------------
        update the other services about the changed calibration
        ------------------
        """
        # await backend_client.update_calibration_info(target_hom_matrix)
        # await waypoint_manager_client.update_calibration_info(target_hom_matrix)
        # asyncio.gather(backend_client.update_calibration_info(target_hom_matrix),
        #                waypoint_manager_client.update_calibration_info(target_hom_matrix))
        """
        ------------------
        Log data
        ------------------
        """
        datalog.hololens_message = hololens_message
        datalog.calibration_position = hologram_position
        datalog.calibration_rotation = hologram_rotation
        datalog.calibration_tracker = ViveTracker(
            ID="cali", location_rotation=tracker_state.calibration_tracker.loc_rot,
            location_tranlation=tracker_state.calibration_tracker.loc_trans)
        datalog.holo_tracker = ViveTracker(
            ID="holo", location_rotation=tracker_state.calibration_tracker.loc_rot,
            location_tranlation=tracker_state.holo_tracker.loc_trans)
        datalog.reprojection_error = reprojection_error
        datalog.real_points = real_cali_points
        datalog.virtual_points = virtual_cali_points
        datalog.calibration_object = str(CALIBRATION_OBJECT)
        """
        ------------------
        Save the log containing the calibration to file
        ------------------
        """
        logger.debug("Starting writing data log to file")
        try:
            datalog.write_to_file()
        except Exception as e:
            import traceback
            logger.error(e)
            logger.error(traceback.format_exc())
        finally:
            # TODO: Save the config into a persistent memory
            queue.task_done()
            logger.info("Task done")


class InformationProcessor():

    async def process_hololens_data(self, message_container: List[str]) -> Tuple[List[float], List[float]]:
        """ this method takes the data received from the hololens and processes
        into a data format which can be processed furhter

        The data may either be :
        1. trans+quat
        2. 3 rows of 4 elements =>rotationmatrix
        3. list of n points

        The transmission format is as follows:
        1. "x,y,z:i,j,k,w|x,y,z:i,j,k,w|....X"


        There may be an number of additional line breaks at the end => strip them off

        Args:
            message_container (str): list of all the data transmitted to us

        Returns:
            np.ndarray: a list of n points
        """
        self.message_received = message_container
        # if there are, join the individual list entries
        message = "".join(message_container)
        # the last element should be "X" thus consider only until that
        message = message.split("X")[0]
        # there is no need to error handling before the next operations
        # because the received job has to be a string that contains end
        # otherwise the tcp ip client wouldnt have put it into the queue
        # hence the above operation can not fail
        logger.debug(f"the message after formatting and transforming: {message}")
        # split the message into indivudal components
        poses = message.split("|")
        position_list = list()
        rotation_list = list()
        for individual_pose in poses:
            position, rotation = await self._process_individual_information(individual_pose)
            position_list.append(position)
            # need to change to scalar first for averaging
            i, j, k, w = rotation
            rotation_list.append([w, i, j, k])
        mean_pos = np.mean(np.array(position_list), axis=0).tolist()
        [w, i, j, k] = averageQuaternions(Q=np.array(rotation_list)).tolist()
        mean_quat = [i, j, k, w]
        return mean_pos, mean_quat

    async def _process_individual_information(self, message: str) -> Tuple[List[float], List[float]]:
        """this method takes a string (potentially representing a transformation and attempts
        to transform it into position, rotation

            expected format:
                x,y,z:i,j,k,w

        Args:
            message (str): message candidate

        Raises:
            IncorrectMessageFormat: if doesnt conform to expected format

        Returns:
            Tuple[List[float], List[float]]: position, rotation
        """
        try:
            position = message.split(":")[0].split(",")
            rotation = message.split(":")[1].split(",")
        except IndexError as e:
            logger.error(f"Received Message: {message} had an IndexError {e}")
            raise IncorrectMessageFormat

        if len(position) != 3 or len(rotation) != 4:
            logger.error(
                f"Received Message: {message} doesnt contain proper position/rotation")
            raise IncorrectMessageFormat
        try:
            position = [float(x) for x in position]
            rotation = [float(x) for x in rotation]
        except ValueError as e:
            logger.error(
                f"Received Message: {message} contains objets not transformable into numbers")
            raise IncorrectMessageFormat
        return position, rotation
