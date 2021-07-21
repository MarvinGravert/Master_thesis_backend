import time
from typing import Dict, Any, Tuple, List

from loguru import logger
import numpy as np

from backend_api.grpc_objects import Controller, Tracker
from modules.poller.base_poller import BasePoller


class MockPoller(BasePoller):
    def start(self):
        logger.info(f"MockPoller is starting")

    def poll(self) -> Tuple[List[Tracker], List[Controller]]:
        """ Create fake polling data
        """
        tracker_list = list()
        controller_list = list()
        """
            ----------
            Controller
            ----------
        """
        button_state = {
            'trackpad_x': 0.4,
            'trackpad_y': 0.2,
            'trackpad_pressed': False,
            'trigger': False,
            'trackpad_touched': False,
            'grip_button': False,
            'menu_button': False
        }
        button_state = {key: str(value) for key, value in button_state.items()}
        logger.debug(button_state)
        controller_list.append(Controller(
            name="mainController",
            rotation=[0, 1, 0, 0],
            position=np.random.randint([10, 10, 10]),
            button_state=button_state)
        )

        """
            ----------
            Holo Tracker
            ----------
        """
        # get the position and rotation
        tracker_list.append(Tracker(
            name="holoTracker",
            rotation=[0, 1, 0, 0],
            position=[1, 0, 2],)
        )

        """
            ----------
            Calibration Tracker
            ----------
        """
        # get the position and rotation
        tracker_list.append(Tracker(
            name="calibrationTracker",
            rotation=[0, 1, 0, 0],
            position=[1, 0, 2],))

        return tracker_list, controller_list
