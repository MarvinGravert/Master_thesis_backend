"""module to process the message received from the hololens into a pose (of the calibration object)
to be used in further processing

Raises:
    IncorrectMessageFormat: if the message doesnt align to predefined format

"""
from backend_api.grpc_objects import Pose
from typing import List, Tuple

import numpy as np
from loguru import logger
from more_itertools import grouper
from backend_api.exceptions import IncorrectMessageFormat
from backend_utils.averageQuaternion import averageQuaternions

from backend_api.general import Waypoint, InterpolationType


class InformationProcessor():

    async def process_hololens_data(self, message_container: List[str]) -> Tuple[List[Pose], List[Pose]]:
        """ this method takes the data received from the hololens and processes
        into a data format which can be processed furhter


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
        # because the received job has to be a string that contains "X"
        # otherwise the tcp ip client wouldnt have put it into the queue
        # hence the above operation can not fail
        logger.debug(f"the message after formatting and transforming: {message}")
        # split the message into indivudal components
        poses = message.split("|")

        trackable_pose_list = list()
        virtual_pose_list = list()
        for real_pose, virtual_pose in grouper(poses, 2):
            # tracker KOS right handed
            position, rotation = await self._process_individual_information(real_pose)
            trackable_pose_list.append(Pose(position=position, rotation=rotation))
            # hololens world KOS left handed
            position, rotation = await self._process_individual_information(virtual_pose)
            virtual_pose_list.append(Pose(position=position, rotation=rotation))

        return trackable_pose_list, virtual_pose_list

    async def process_path_information(self, message_container: str) -> List[Waypoint]:
        """process the path Informatoin from hololens into into a robot path
             structered as such:
             position:orientation|interpolationtype$position.....
             position=x,y,z
             orientation=i,j,k,w
             interpolationtype=> Linear or PTP potentially added more in future
        Args:
            message (str): list of all the data transmitted to us
        """
        self.message_received = message_container
        # if there are, join the individual list entries
        message = "".join(message_container)
        # the last element should be "X" thus consider only until that
        message = message.split("X")[0]
        # there is no need to error handling before the next operations
        # because the received job has to be a string that contains "X"
        # otherwise the tcp ip client wouldnt have put it into the queue
        # hence the above operation can not fail
        logger.debug(f"the message after formatting and transforming: {message}")
        # split the message into indivudal waypoints
        waypoints_as_string = message.split("$")

        path_point_list: List[Waypoint] = list()
        for waypoint in waypoints_as_string:
            # split into interpolation and pose
            pose, interpolation = waypoint.split("|")
            position, rotation = await self._process_individual_information(pose)

            inter_type = InterpolationType(interpolation)
            path_point_list.append(Waypoint(
                position=np.array(position),
                rotation=np.array(rotation),
                type=inter_type
            ))

        return path_point_list

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
