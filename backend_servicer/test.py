from holoViveCom_pb2 import LighthouseState, HandheldController
import holoViveCom_pb2_grpc
from loguru import logger
import grpc
import asyncio
from config.const import (
    WAYPOINT_MANAGER_HOST, WAYPOINT_MANAGER_PORT
)


async def notify_way_point():
    """this method notifies the way point manager that the menu button has been
    pressed and thus a waypoint shall be placed.
    Along with this the controller position is passed
    """
    logger.info("Starting Connection to waypoint manager")
    async with grpc.aio.insecure_channel(f"{WAYPOINT_MANAGER_HOST}:{WAYPOINT_MANAGER_PORT}") as channel:
        logger.info(
            f"Started communicator")
        stub = holoViveCom_pb2_grpc.BackendStub(channel=channel)
        """
            Build the message and send
            """
        controller_obj = HandheldController(ID="iji")
        logger.debug(f"Sending: {controller_obj}")
        reply = stub.PlaceWayPoint(LighthouseState(controller=controller_obj))

    logger.info("Way point manager has been notified")
    return True


async def main():
    asyncio.gather(notify_way_point())

asyncio.run(main())
