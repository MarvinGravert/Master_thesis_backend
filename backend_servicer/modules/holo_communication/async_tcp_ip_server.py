import asyncio
import struct
from asyncio.streams import StreamReader, StreamWriter

from loguru import logger

from config.api_types import VRState


class TcpIPServer():
    def __init__(self, IP: str, port: int, vr_state: VRState):
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
        await self.vr_state._controller_set_event.wait()  # wait till  VRObjects are init
        data = await reader.read(100)
        message = data.decode()
        logger.debug(self.vr_state.controller._button_state)
        # some debugging information
        addr = writer.get_extra_info('peername')
        logger.debug(f"Received {message!r} from {addr!r}")
        # now just keep communication open while always responding with the latest
        # controller state upon received request
        while True:

            data = await reader.read(100)
            message = data.decode()
            logger.debug(f"received: {message}")
            # message should be irrelevant hence
            data = self._get_data_to_send()
            logger.debug(f"Send: {data!r}")  # turn data back into readable string
            writer.write(data)
            await writer.drain()

    def _get_data_to_send(self) -> bytes:
        # Prepare to send in format x,y,z:w,i,j,k:x_trackpad:trigger,trackpad_pressed, menuButton,grip_button:status

        controller_state = self.vr_state.controller.get_state_as_string()
        status: str = "some message"
        message = bytes(controller_state+":"+status, "utf-8")
        data_to_send = struct.pack(f"{len(message)}s", message)
        return data_to_send
