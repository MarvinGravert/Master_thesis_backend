import asyncio
import struct
from asyncio.streams import StreamReader, StreamWriter

from typing import List, Dict


from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R

from api.general_types import ServerState, MessageObject, Tracker, Controller


class TcpIPServer():
    def __init__(self, IP: str, port: int, server_state: ServerState):
        self.IP = IP
        self.port = port
        self.server_state = server_state

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
        Format: tracker1|...|trackerN$controller1|...|controllerN$command\n

        TODO: function is suboptimal =>optimize later
        having to loop twice 1. from mgs_dict and then from list=> bad scaling
        Returns:
            bytes: data in bytes
       """

        command: str = self.server_state.message_obj_dict["command"]
        tracker_list: List[Tracker] = []
        controller_list: List[Controller] = []
        for ele in self.server_state.message_obj_dict.values():
            if isinstance(ele, Tracker):
                tracker_list.append(ele)
            if isinstance(ele, Controller):
                controller_list.append(ele)
        state = "|".join([tracker.as_string for tracker in tracker_list])
        state = state[-1]+"$"
        state += "|".join([controller.as_string for controller in controller_list])
        state = state[-1]+"$"
        state += command
        message = bytes(command+"\n", "utf-8")

        data_to_send = struct.pack(f"{len(message)}s", message)
        return data_to_send
