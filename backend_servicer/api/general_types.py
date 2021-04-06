from typing import Any, Dict, List
import asyncio

from loguru import logger
from scipy.spatial.transform import Rotation as R
import numpy as np

from holoViveCom_pb2 import (
    HandheldController, Tracker, CalibrationInfo
)
from backend_api.general import Calibration

from backend_api.vr_objects import (
    ViveController, ViveTracker
)


class ServerState():
    """object who keeps track of the system state
    this includes:
    - Both trackers (holo and calibration)
    - controller (pose +button)
    - status (mainly used for debugging)
    - Calibration

    it provides the following functionalites:

    """

    def __init__(self):
        self.init_vr_objects()
        self.calibration = Calibration()
        self._status: str = "no_status"
        self.new_full_state_subscriber: Dict[str, asyncio.Event] = dict()
        self.new_tracker_state_subscriber: Dict[str, asyncio.Event] = dict()

    @ property
    def holo_tracker(self) -> ViveTracker:
        return self._holo_tracker

    @ holo_tracker.setter
    def holo_tracker(self, new_tracker: ViveTracker):
        self._holo_tracker = new_tracker

    @ property
    def calibration_tracker(self) -> ViveTracker:
        return self._calibration_tracker

    @ calibration_tracker.setter
    def calibration_tracker(self, new_tracker: ViveTracker):
        self._calibration_tracker = new_tracker

    @ property
    def controller(self) -> ViveController:
        return self._controller

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, new_status: str) -> None:
        self._status = new_status

    @ controller.setter
    def controller(self, new_controller: ViveController):
        self._controller = new_controller

    def update_holo_tracker(self, new_state: Tracker) -> None:
        logger.debug("Updating HoloTracker")
        self._holo_tracker.update_state(new_state)

    def update_calibration_tracker(self, new_state: Tracker) -> None:
        logger.debug("Updating CaliTracker")
        self._calibration_tracker.update_state(new_state)

    def update_controller(self, new_state: HandheldController) -> None:
        logger.debug("Updating Controller")
        self._controller.update_state(new_state)

    def init_vr_objects(self):
        logger.debug("Initing vr objects")
        zero_position = [0, 0, 0]
        zero_rotation = [1, 0, 0, 0]
        zero_button_state = {
            "trackpad_x": "0.0",
            "trackpad_y": "0.0",
            "trackpad_pressed": "False",
            "trigger": "False",
            "menu_button": "False",
            "grip_button": "False"
        }
        self._holo_tracker = ViveTracker(rotation=zero_rotation,
                                         position=zero_position)

        self._calibration_tracker = ViveTracker(rotation=zero_rotation,
                                                position=zero_position)
        self._controller = ViveController(rotation=zero_rotation,
                                          position=zero_position,
                                          button_state=zero_button_state)
