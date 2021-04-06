import time
from typing import Dict, Any

from loguru import logger
import numpy as np

from backend_api.vr_objects import VRObject, ViveController, ViveTracker

from modules.poller.base_poller import BasePoller


class MockPoller(BasePoller):
    def start(self):
        logger.info(f"MockPoller is starting")

    def poll(self) -> Dict[str, Any]:
        """ Poll the Lighthouse for each object
        if its found add its data to a dictionnary which is passed back
        """
        state_dict = dict()
        """
            ----------
            Controller
            ----------
        """
        button_state = {
            'trackpad_x': 0.4,
            'trackpad_y': 0.2,
            'trackpad_pressed': False,
            'trigger': 0.6,
            'trackpad_touched': False,
            'grip_button': False,
            'menu_button': False
        }
        button_state = {key: str(value) for key, value in button_state.items()}
        state_dict["controller"] = ViveController(
            rotation=[0, 1, 0, 0],
            position=np.random.randint([10, 10, 10]),
            button_state=button_state).get_as_grpc_object()

        """
            ----------
            Holo Tracker
            ----------
        """
        # get the position and rotation
        state_dict["holo_tracker"] = ViveTracker(
            rotation=[0, 1, 0, 0],
            position=[1, 0, 2],).get_as_grpc_object()

        """
            ----------
            Calibration Tracker
            ----------
        """
        # get the position and rotation
        state_dict["calibration_tracker"] = ViveTracker(
            rotation=[0, 1, 0, 0],
            position=[1, 0, 2],).get_as_grpc_object()

        return state_dict
