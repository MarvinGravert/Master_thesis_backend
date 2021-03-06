"""this modules coordinates all the information and communication necessary to find the correspondacne beetween lighthsoue
world and hololens world

it does so utliizing asnyc whereever necessary
"""
import asyncio
from typing import List

import numpy as np
from loguru import logger

from config.const import (
    POINT_REGISTER_HOST, POINT_REGISTER_PORT, BACKEND_HOST, BACKEND_PORT
)
from modules.communication.grpc_client import BackendCommunicator, PointRegisterCommunicator
from modules.point_correspondance.find_point_corresponder import get_points_real_object, get_points_virtual_object
from config.api_types import IncorrectMessageFormat


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
    """
    ------------------
    Start the services
    ------------------
    """
    while True:
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
            virtual_cali_points = await info_processor.process_hololens_data(hololens_message)
        except IncorrectMessageFormat:
            logger.error("Message has the incorrect format. Dicarding job")
            queue.task_done()
            continue

        real_cali_points = get_points_real_object(
            vive_trans=np.array(tracker_state.calibration_tracker.loc_trans),
            vive_rot=np.array(tracker_state.calibration_tracker.loc_rot)
        )
        """
        ------------------
        calculate point registering
        ------------------
        """
        hom_matrix_virtual_to_LH = await points_register_client.register_points(
            point_set_1=real_cali_points,
            point_set_2=virtual_cali_points
        )
        logger.info(f"Transformtion-Matrix: LH to virtual center:\n {hom_matrix_virtual_to_LH} ")
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
        # now e can get the transformatoin from the virtual cetner to the vive tracker
        target_hom_matrix = hom_matrix_virtual_to_LH@tracker_hom_matrix
        logger.info(
            f"The transformation matrix:  virutal center to tracker is:\n {target_hom_matrix}")
        """
        ------------------
        update the other services about the changed calibration
        ------------------
        """
        await backend_client.update_calibration_info(target_hom_matrix)
        """
        ------------------
        Save the calibration to file
        ------------------
        """
        # TODO: Save the config into a persistent memory
        queue.task_done()


class InformationProcessor():

    async def process_hololens_data(self, message_container: List[str]) -> np.ndarray:
        """ this method takes the data received from the hololens and processes
        into a data format which can be processed furhter

        The data may either be :
        1. trans+quat
        2. 3 rows of 4 elements =>rotationmatrix
        3. list of n points

        The transmission format is as follows:
        1. "x,y,z:w,i,j,k"
        2. "x11,x12,x13,x14\nx21,x22,x23,x24\nx31,x32,x33,x34"
        3. "x11,x12,x13\nx21,x22,x23\n.....xn1,xn2,xn3\n"

        There may be an number of additional line breaks at the end => strip them off

        Args:
            message_container (str): list of all the data transmitted to us

        Returns:
            np.ndarray: a list of n points
        """
        # if there are, join the individual list entries
        message = "".join(message_container)
        # the last element should be "end" thus consider only until that
        message = message.split("end")[0]
        # there is no need to error handling before the next operations
        # because the received job has to be a string that contains end
        # otherwise the tcp ip client wouldnt have put it into the queue
        # hence the above operation can not fail
        logger.debug(f"the message after formatting and transforming: {message}")
        # split the message into indivudal components
        try:
            position = message.split(":")[0].split(",")
            rotation = message.split(":")[1].split(",")
        except IndexError as e:
            logger.error(f"Received Message: {message_container} had an IndexError {e}")
            raise IncorrectMessageFormat

        if len(position) != 3 or len(rotation) != 4:
            logger.error(
                f"Received Message: {message_container} doesnt contain proper position/rotation")
            raise IncorrectMessageFormat
        try:
            position = [float(x) for x in position]
            rotation = [float(x) for x in rotation]
        except ValueError as e:
            logger.error(
                f"Received Message: {message_container} contains objets not transformable into numbers")
            raise IncorrectMessageFormat
        return get_points_virtual_object(unity_trans=position, unity_rot=rotation)
