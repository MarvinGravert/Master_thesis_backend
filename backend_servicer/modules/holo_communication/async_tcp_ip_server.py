import asyncio
import struct
from asyncio.streams import StreamReader, StreamWriter
from typing import List
from holoViveCom_pb2 import Quaternion

from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R

from api.general_types import ServerState


class TcpIPServer():
    def __init__(self, IP: str, port: int, vr_state: ServerState):
        self.IP = IP
        self.port = port
        self.vr_state = vr_state

    async def start(self):
        logger.info(f"Async TCP/IP Server is starting on {self.IP}:{self.port}")
        server = await asyncio.start_server(self.communicate_hololens, self.IP, self.port)
        addr = server.sockets[0].getsockname()
        logger.debug(f"Serving on {addr}")

        async with server:
            await server.serve_forever()

    async def communicate_hololens(self, reader: StreamReader, writer: StreamWriter):
        # wait to receive a message => shows that the hololens wants to know the state
        # of the controller
        # some debugging information
        addr = writer.get_extra_info('peername')
        logger.info(f"Received connetion from {addr!r}")
        # now just keep communication open while always responding with the latest
        # controller state upon received request
        while True:
            data = await reader.read(100)
            message = data.decode()
            logger.debug(f"received: {message}")
            if "X" not in message:
                break  # hacky fix to stop receving a million messsages when unity turns off
            # message should be irrelevant hence
            data = self._get_data_to_send()
            logger.debug(f"Send: {data!r}")  # turn data back into readable string
            writer.write(data)
            await writer.drain()

    def _get_data_to_send(self) -> bytes:
        """builds the reponse which is to be sent the hololens
        There are two cases:
        1. No calibration: Simply sent the data from the lighthouse directly
        2. Calibration set: Calculate the controller position in hololens world using this

        in both cases the systemStatus is also attached

        Returns:
            bytes: data in bytes
        """
        if False:  # self.vr_state.calibration.calibration_received():#TODO: integrate calibration
            controller_pose: List[np.ndarray] = self._calculate_post_calibration_controller_pose()
            controller_button_state: str = self.vr_state.controller.get_button_state_as_string()
            controller_state: str = self._turn_pose_into_string(pose=controller_pose) +\
                ":"+controller_button_state
        else:
            controller_state: str = self.vr_state.controller.get_state_as_string()

        status: str = self.vr_state.status
        message = bytes(controller_state+":"+status+"\n", "utf-8")
        data_to_send = struct.pack(f"{len(message)}s", message)
        return data_to_send

    def _calculate_post_calibration_controller_pose(self) -> List[np.ndarray]:
        """calculate the controller position using the calibration wihch has been set

        For this we need to do several matrix multiplications:
        the transformation traversal is as follows:
        controller->inverse(holoTracker)->inverse(Calibration)

        Controller->Lh->HoloTracker->hololens (essentially stating the KOS we go across)

        NOTE: for debugging purposes the inverse will be calculated everytime
        this will be removed in the final version (probably)#TODO:

        Returns:
            List[np.ndarray]: [position,rotation]
        """
        controller_hom_matrix = self.vr_state.controller.get_pose_as_hom_matrix()
        holo_tracker_hom_matrix = self.vr_state.holo_tracker.get_pose_as_hom_matrix()
        holo_to_tracker_calibration_hom_matrix = self.vr_state.calibration.calibration_matrix

        controller_to_hololens = np.linalg.inv(holo_to_tracker_calibration_hom_matrix)\
            @ np.linalg.inv(holo_tracker_hom_matrix) @ controller_hom_matrix

        # seperate out the position and rotation (as quaternion)

        rot_matrix = controller_to_hololens[:3, :3]
        quaternion_rot = R.from_matrix(rot_matrix).as_quat()
        # vive normally transmits scalar first hence we need to adjust
        i, j, k, w = quaternion_rot
        position = controller_to_hololens[:3, 3]
        return [position, np.array([w, i, j, k])]

    def _turn_pose_into_string(self, pose: List[np.ndarray]) -> str:
        """turn the received pose into a string
        format: x,y,z:w,i,j,k 

        Args:
            pose (List[float]): [position,rotation as quaternion]

        Returns:
            str: [description]
        """
        s = ",".join([str(i) for i in pose[0]])+":"
        s += ",".join([str(i) for i in pose[1]])
        return s
