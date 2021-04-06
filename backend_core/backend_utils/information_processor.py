"""module to process the message received from the hololens into a pose (of the calibration object)
to be used in further processing

Raises:
    IncorrectMessageFormat: if the message doesnt align to predefined format

"""
from typing import List, Tuple

import numpy as np
from loguru import logger

from backend_api.exceptions import IncorrectMessageFormat
from backend_utils.averageQuaternion import averageQuaternions


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
