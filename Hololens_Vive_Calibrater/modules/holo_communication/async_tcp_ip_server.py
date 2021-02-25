import asyncio
import struct
from asyncio.streams import StreamReader, StreamWriter

from loguru import logger

from config.api_types import VRState


class TcpIPServer():
    def __init__(self, IP: str, port: int):
        self.IP = IP
        self.port = port

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
        # await self.vr_state._initialized.wait()  # wait till  VRObjects are init
        data = await reader.read(100)
        message = data.decode()

        # some debugging information
        addr = writer.get_extra_info('peername')
        logger.info(f"Received connection from {addr}")
        # now just keep communication open while always responding with the latest
        # controller state upon received request
        while True:

            data = await reader.read(100)
            message = data.decode()
            logger.debug(f"received: {message}")
            # message should be irrelevant hence
            data = b"s"
            writer.write(data)
            await writer.drain()
