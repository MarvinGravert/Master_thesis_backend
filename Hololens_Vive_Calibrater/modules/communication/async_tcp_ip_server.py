import asyncio
import struct
from asyncio.streams import StreamReader, StreamWriter

from loguru import logger

import numpy as np


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

        # some debugging information
        addr = writer.get_extra_info('peername')
        logger.info(f"Received connection from {addr}")
        # now just read the data into a data container and cancel the connection
        # upon the reception of "end"
        message_container = list()
        while True:
            data = await reader.read(100)
            message = data.decode()
            logger.debug(f"received: {message}")
            message_container.append(message)
            if "end" in message:  # using some message to signal the end of data transmission
                break
            # return message is  irrelevant hence random string
            data = b"s"
            writer.write(data)
            await writer.drain()
            # we will exit this when the outside connection breaks
        await self.queue.put(message_container)
        logger.debug(f"Put message into queue: {message_container}")
