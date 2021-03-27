from typing import Any, Dict, List
import asyncio

from loguru import logger
from scipy.spatial.transform import Rotation as R
import numpy as np

from holoViveCom_pb2 import (
    HandheldController, Tracker, CalibrationInfo
)

from api.vr_types import (
    ViveController, ViveTracker
)


class Calibration():
    """representation of the calibration matrix which maps from virtual to tracker
    it saves this as a homogenous matrix which can be usd in processing

    Furthermore, a boolean is used to check if calibration has been set as this 
    is simply initialised with an empty calibration
    """

    def __init__(self):
        """initialise the matrix with the base homogenous matrix
        """
        LH_2_virtual_center = """
        1 0 0 0
        0 1 0 0
        0 0 1 0
        0 0 0 1
        """
        self._calibration_matrix: np.ndarray = np.fromstring(LH_2_virtual_center,
                                                             dtype=float,
                                                             sep=" ").reshape((4, 4))
        self._calibration_received: bool = False

    @property
    def calibration_matrix(self) -> np.ndarray:
        return self._calibration_matrix

    def set_calibration_via_grpc_object(self, calibration_info: CalibrationInfo) -> None:
        """setting the calibration matrix when handed via gprc_object

        the object is a flattend 4x4 matrix

        Args:
            calibration_info (CalibrationInfo): [description]
        """
        flattend_matrix: List[float] = calibration_info.calibrationMatrixRowMajor
        self._calibration_matrix = np.array(flattend_matrix).reshape([4, 4])
        logger.debug(f"New calibration has been set to: \n {self.calibration_matrix}")
        # This signifies a received calibration
        self._calibration_received = True

    def get_calibration_as_grpc_object(self) -> CalibrationInfo:
        """returns the calibration matrix as a calibrationInfo gRPC object
        the matrix is simply flattend

        Returns:
            CalibrationInfo: grpc object has definedin proto
        """
        return CalibrationInfo(calibrationMatrixRowMajor=self.calibration_matrix.flatten())

    def calibration_received(self) -> bool:
        return self._calibration_received


class VRState():
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
