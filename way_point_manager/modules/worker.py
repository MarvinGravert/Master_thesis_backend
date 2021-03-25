
"""this modules coordinates all the information and communication necessary to find the correspondacne beetween lighthsoue
world and hololens world

it does so utliizing asnyc whereever necessary
"""
import asyncio
from typing import List

import numpy as np
from loguru import logger

from config.const import (
    BACKEND_HOST, BACKEND_PORT
)


async def worker(queue: asyncio.Queue):
    # Start server
    logger.info("Worker has started")

    """
    ------------------
    Start the services
    ------------------
    """
    while True:

        hololens_message: List[str] = await queue.get()
        logger.info("New job has arrived. Start processing")
        # now we can get the data from the trackers
        tracker_state = await backend_client.get_tracker_pose()
        # now  we can process the response we received from the hololens
        logger.debug("received information from trackers, now process information")
        """
        ------------------
        work through the messages
        ------------------
        """
        info_processor = InformationProcessor()
        try:
            hologram_position, hologram_rotation = await info_processor.process_hololens_data(hololens_message)

        except IncorrectMessageFormat:
            logger.error("Message has the incorrect format. Dicarding job")
            queue.task_done()
            continue

        """
        ------------------
        get the point correspondances
        ------------------
        """
        virtual_cali_points = get_points_virtual_object(
            unity_trans=hologram_position, unity_rot=hologram_rotation)
        real_cali_points = get_points_real_object(
            vive_trans=tracker_state.calibration_tracker.loc_trans,
            vive_rot=tracker_state.calibration_tracker.loc_rot
        )
        """
        ------------------
        calculate point registering
        ------------------
        """
        reprojection_error, hom_matrix_LH_to_virtual = await points_register_client.register_points(
            point_set_1=real_cali_points,
            point_set_2=virtual_cali_points
        )
        logger.info(f"Transformtion-Matrix: LH to virtual center:\n {hom_matrix_LH_to_virtual} ")
        datalog.hom_LH_to_virtual = hom_matrix_LH_to_virtual
        """
        ------------------
        get tracker transformation
        ------------------
        """
        tracker_hom_matrix = tracker_state.holo_tracker.get_as_hom_matrix()
        """
        ------------------
        calculate desired transformation
        ------------------
        """
        # now e can get the transformatoin from the tracker to the virtual center
        target_hom_matrix = hom_matrix_LH_to_virtual@tracker_hom_matrix
        logger.info(
            f"The transformation matrix:  tracker to virtual is:\n {target_hom_matrix}")
        datalog.hom_tracker_to_virtual = target_hom_matrix
        """
        ------------------
        update the other services about the changed calibration
        ------------------
        """
        # await backend_client.update_calibration_info(target_hom_matrix)
        # await waypoint_manager_client.update_calibration_info(target_hom_matrix)
        # asyncio.gather(backend_client.update_calibration_info(target_hom_matrix),
        #                waypoint_manager_client.update_calibration_info(target_hom_matrix))
        """
        ------------------
        Log data
        ------------------
        """
        datalog.hololens_message = hololens_message
        datalog.calibration_position = hologram_position
        datalog.calibration_rotation = hologram_rotation
        datalog.calibration_tracker = ViveTracker(
            ID="cali", location_rotation=tracker_state.calibration_tracker.loc_rot,
            location_tranlation=tracker_state.calibration_tracker.loc_trans)
        datalog.holo_tracker = ViveTracker(
            ID="holo", location_rotation=tracker_state.calibration_tracker.loc_rot,
            location_tranlation=tracker_state.holo_tracker.loc_trans)
        datalog.reprojection_error = reprojection_error
        datalog.real_points = real_cali_points
        datalog.virtual_points = virtual_cali_points
        datalog.calibration_object = str(CALIBRATION_OBJECT)
        """
        ------------------
        Save the log containing the calibration to file
        ------------------
        """
        logger.debug("Starting writing data log to file")
        try:
            datalog.write_to_file()
        except Exception as e:
            import traceback
            logger.error(e)
            logger.error(traceback.format_exc())
        finally:
            # TODO: Save the config into a persistent memory
            queue.task_done()
            logger.info("Task done")
