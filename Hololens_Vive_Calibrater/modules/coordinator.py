"""this modules coordinates all the information and communication necessary to find the correspondacne beetween lighthsoue
world and hololens world

it does so utliizing asnyc whereever necessary
"""
import asyncio

import numpy as np
from loguru import logger

from config.const import (
    TCP_HOST, TCP_PORT, POINT_REGISTER_HOST, POINT_REGISTER_PORT, BACKEND_HOST, BACKEND_PORT
)
from modules.communication.async_tcp_ip_server import TcpIPServer
from modules.communication.grpc_client import BackendCommunicator, PointRegisterCommunicator
from modules.point_correspondance.find_point_corresponder import get_points_real_object, get_points_virtual_object


class Coordinator():
    async def pipeline():
        # Start server
        logger.info("Pipeline coordinateor has started")
        """
        ------------------
        SETTING UP THE IPs
        ------------------
        """
        tcp_host_ip = TCP_HOST
        tcp_host_port: int = TCP_PORT
        backend_host_ip = BACKEND_HOST
        backend_host_port = BACKEND_PORT
        points_register_host_ip = POINT_REGISTER_HOST
        points_register_host_port = POINT_REGISTER_PORT
        """
        ------------------
        Start the services
        ------------------
        """
        tcp_server = TcpIPServer(IP=tcp_host_ip, port=tcp_host_port)
        backend_client = BackendCommunicator(backend_host_ip, backend_host_port)
        points_register_client = PointRegisterCommunicator(
            points_register_host_ip, points_register_host_port)

        await tcp_server.start()
        await tcp_server.updated_batch.wait()  # wait until we received a batch
        logger.info("we received info from hololens now get info from trackers")
        # now we can get the data from the trackers
        tracker_state = await backend_client.get_tracker_pose()
        # now  we can process the rsponse we received from the hololens
        logger.info("receviing information from trackers, do some messgae prep on holo messages")
        holo_message = tcp_server._current_message_batch

        """
        ------------------
        work through the messages
        ------------------
        """
        info_processor = InformationProcessor()
        virtual_cali_points = await info_processor.process_hololens_data(holo_message)
        real_cali_points = get_points_real_object(
            vive_trans=tracker_state.calibration_tracker.loc_trans,
            vive_rot=tracker_state.calibration_tracker.loc_rot
        )
        """
        ------------------
        calculate point registering 
        ------------------
        """
        hom_matrix_virtual_to_LH = await points_register_client.register_points(
            point_set_1=virtual_cali_points,
            point_set_2=real_cali_points
        )
        logger.info(f"Virtual to LH Matrix: {hom_matrix_virtual_to_LH} ")
        """
        ------------------
        get tracker transformation
        ------------------
        """
        tracker_hom_matrix = tracker_state.holo_tracker.get_as_hom_matrix()
        # now e can get the transformatoin from the virtual cetner to the vive tracker
        target_hom_matrix = np.linalg.inv(tracker_hom_matrix)@hom_matrix_virtual_to_LH
        logger.info(
            f"The transformatoin matrix from virutal center to trakcer is:\n {target_hom_matrix}")


class InformationProcessor():

    async def process_hololens_data(self, message_container: str) -> np.ndarray:
        """ this method takes the data received from the hololens and processes 
        into a data format which can be processed furhter

        The data may either be :
        1. trans+quat
        2. 3 rows of 4 elements =>rotationmatrix
        3. list of n points

        The transmission format is as follows:
        1. "x,y,z,w,i,j,k"
        2. "x11,x12,x13,x14\nx21,x22,x23,x24\nx31,x32,x33,x34"
        3. "x11,x12,x13\nx21,x22,x23\n.....xn1,xn2,xn3\n"

        There may be an number of additional line breaks at the end => strip them off

        Args:
            message_container (str): list of all the data transmitted to us 

        Returns:
            np.ndarray: a transformation matrix OR a list of n points
        """
        return np.empty([4, 4])
