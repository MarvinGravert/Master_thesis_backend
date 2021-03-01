import asyncio
import struct
from asyncio.streams import StreamReader, StreamWriter

from loguru import logger

import numpy as np


class TcpIPServer():
    def __init__(self, IP: str, port: int):
        self.IP = IP
        self.port = port
        # synchronize information (if new batch is being read into this will stop processing on the current batch)
        self.updated_batch = asyncio.Event()
        self._current_message_batch: str = ""

    async def start(self):
        logger.info(f"Async TCP/IP Server is starting on {self.IP}:{self.port}")
        server = await asyncio.start_server(self.communicate_hololens, self.IP, self.port)
        addr = server.sockets[0].getsockname()
        logger.debug(f"Serving on {addr}")

        async with server:
            await server.serve_forever()

    async def communicate_hololens(self, reader: StreamReader, writer: StreamWriter):
        # wait for the hololens to connect and accept its data

        # some debugging information
        addr = writer.get_extra_info('peername')
        logger.info(f"Received connection from {addr}")
        # now just read the data into a data container and cancel the connection up the reception of a double
        # line break in a single message
        # synchronize the update using an asyncio.Evetn
        message_container = list()
        self.updated_batch.clear()
        while True:
            data = await reader.read(100)
            message = data.decode()
            logger.debug(f"received: {message}")
            message_container.append(message)
            if message == "\n\n" or message[-2:] == "\n\n":
                break
            # message should be irrelevant hence
            data = b"s"
            writer.write(data)
            await writer.drain()
            # we will exit this when the outside connection breaks
        self._current_message_batch = message_container
        self.updated_batch.set()

        logger.debug(f"Saved message: {self._current_message_batch}")
