
"""this modules coordinates all the information and communication necessary to find the correspondacne beetween lighthsoue
world and hololens world

it does so utliizing asnyc whereever necessary
"""
import asyncio
from typing import List, Union
from backend_api.general import Waypoint

import numpy as np
from loguru import logger
from scipy.spatial.transform import Rotation as R


from backend_utils.information_processor import InformationProcessor

from config.api_types import ServerState
from backend_api.exceptions import IncorrectMessageFormat


class WorkerClass():
    def __init__(self) -> None:
        self.information_processor = InformationProcessor()

    async def worker(self, queue: asyncio.Queue, server_state: ServerState):
        # Start server
        logger.info("Worker has started")
        self.server_state = server_state
        """
        ------------------
        Start the services
        ------------------
        """
        while True:
            hololens_message: List[str] = await queue.get()
            logger.info("New path has arrived. Start processing")
            # first we can get the data from the trackers
            """
                ------------------
               PATH processing
                ------------------
            """
            try:

                # Path
                path: List[Waypoint] = await self.information_processor.process_path_information(hololens_message)

            except IncorrectMessageFormat:
                logger.error("Message has the incorrect format. Dicarding job")
                queue.task_done()
                continue
            for waypoint in path:
                waypoint.apply_offset(np.array([0, -0.0145, 0.1735]))  # offset in m!
            logger.info(f"The path is:\n {path}")

            """
            ------------------
            Transform all waypoints into robot workspace
            ------------------
            The received waypoints are the ones taken in the vive lighthouse 
            and not transformed thus no correction for lefthanded or righthanded has to be applied 
            """

            hom_matrix = self.server_state.hom_matrix_LH_Robo
            for waypoint in path:
                point_in_robo = hom_matrix@np.append(waypoint.position, 1)
                logger.info(f"{waypoint.type}: {point_in_robo[:3]}")
