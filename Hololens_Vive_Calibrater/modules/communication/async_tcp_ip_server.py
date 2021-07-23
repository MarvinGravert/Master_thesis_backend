import asyncio
import struct
from asyncio.streams import StreamReader, StreamWriter
from backend_api.grpc_objects import Pose

from loguru import logger

import numpy as np

from config.api import Task


class TcpIPServer():
    def __init__(self, IP: str, port: int, queue: asyncio.Queue):
        self.IP = IP
        self.port = port
        self.queue = queue

    async def start(self):
        logger.info(f"Async TCP/IP Server is starting on {self.IP}:{self.port}")
        try:
            server = await asyncio.start_server(self.communicate_hololens, self.IP, self.port)
        except Exception as e:
            logger.error(e)
            raise
        addr = server.sockets[0].getsockname()
        logger.debug(f"Serving on {addr}")

        async with server:
            await server.serve_forever()

    async def communicate_hololens(self, reader: StreamReader, writer: StreamWriter):
        # wait for the hololens to connect and accept its data
        addr = writer.get_extra_info('peername')
        logger.info(f"Received connection from {addr}")
        # now just read the data into a data container and cancel the connection
        # upon the reception of X
        message_container = list()
        end_connection = False
        try:
            while True:
                data = await reader.read(100)
                message = data.decode()
                logger.debug(f"received: {message}")
                logger.debug(f"data length: {len(message)}")
                if len(message) == 0:  # empty message get read in if the hololens disconnects
                    break
                message_container.append(message)
                if "X" in message:  # using some message to signal the end of data transmission
                    task = Task(message=message_container, callback_event=asyncio.Event())
                    await self.queue.put(task)
                    logger.debug(f"Put message into queue: {message_container}")
                    message_container = []  # clear the container
                    await task.callback_event.wait()
                    data = self._get_data_to_send(task.transformation)
                    writer.write(data)
                    await writer.drain()
                    # break
                # we will exit this when the outside connection breaks
        except ConnectionResetError:
            logger.warning(f"Remote connection {addr} was lost")

    def _get_data_to_send(self, pose: Pose):
        message = bytes(pose.as_string()+"\n", "utf-8")
        data_to_send = struct.pack(f"{len(message)}s", message)
        return data_to_send
