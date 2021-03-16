from typing import Any, Dict, List
import asyncio

from loguru import logger
from scipy.spatial.transform import Rotation as R
import numpy as np

from holoViveCom_pb2 import (
    HandheldController, LighthouseState,  Quaternion, Tracker, CalibrationInfo
)


class VRObject():
    def __init__(self,
                 ID: str,
                 location_rotation: List[float],
                 location_tranlation: List[float]) -> None:
        self.ID = ID
        self.loc_rot = location_rotation  # w i j k
        self.loc_trans = location_tranlation  # x y z

    def get_pose_as_hom_matrix(self) -> np.ndarray:
        """returns the current pose (postion+quat) as a 4x4 homogenous matrix

        Returns:
            np.ndarray: 4x4 homogenous matrix
        """
        w, i, j, k = self.loc_rot
        rot = R.from_quat([i, j, k, w])  # scipy wants scalar last)
        rot_matrix = rot.as_matrix()
        hom_matrix = np.hstack([rot_matrix, np.array(self.loc_trans).reshape([3, 1])])
        return np.vstack([hom_matrix, [0, 0, 0, 1]])


class ViveTracker(VRObject):
    def update_state(self, new_data: Tracker):
        self.loc_rot = new_data.rotation.quat
        self.loc_trans = new_data.position

    def get_as_grpc_object(self) -> Tracker:
        quat = Quaternion(quat=self.loc_rot)
        trans = self.loc_trans
        return Tracker(ID=self.ID, rotation=quat, position=trans)


class ViveController(VRObject):
    def __init__(self,
                 ID: str,
                 location_rotation: List[float],
                 location_tranlation: List[float],
                 button_state: Dict[str, str]) -> None:
        super().__init__(ID, location_rotation, location_tranlation)
        self._button_state = self._adjust_button_states(button_state)
        self._last_state_menu_button = False

    def update_state(self, new_data: HandheldController):
        """updates the internal state of the controller and runs checks on the buttons

        Args:
            new_data (HandheldController): grpc object containing the new data
        """
        self.loc_rot = list(new_data.rotation.quat)
        self.loc_trans = list(new_data.position)
        # run some checks on the received button state
        self._button_state = self._check_and_adjust_button_states(new_data.button_state)

    def _check_and_adjust_button_states(self, button_state: Dict[str, str]) -> Dict[str, str]:
        """Checks for the menu button as well as changes the trigger value from
        float to a bool 

        If the menu button is pressed (False->True) a way point placing is triggered
        """
        if float(button_state['trigger']) < 0.5:
            button_state['trigger'] = "False"
        else:
            button_state['trigger'] = "True"
        if self._last_state_menu_button == True and \
                button_state["menu_button"] == "True":
            pass  # way point placing

        return button_state

    def get_state_as_string(self) -> str:
        """returns the current state (pose+button_state) as a string
        so that it can be passed to the tcp_ip communication

            The format is as follows
            x,y,z:w,i,j,k:x_trackpad,y_trackpad:trigger,trackpad_pressed, menuButton,grip_button

        Returns:
            str: [description]
        """

        x_trackpad = self._button_state["trackpad_x"]
        y_trackpad = self._button_state["trackpad_y"]
        trackpadPressed = self._button_state["trackpad_pressed"]
        triggerButton = self._button_state["trigger"]
        menuButton = self._button_state["menu_button"]
        gripButton = self._button_state["grip_button"]

        s = ",".join([str(i) for i in self.loc_trans])+":"
        s += ",".join([str(i) for i in self.loc_rot])+":"

        s += x_trackpad+","+y_trackpad+":"+triggerButton+","+trackpadPressed+","+menuButton+","+gripButton
        return s

    def get_button_state_as_string(self) -> str:
        """returns the current button state of the controller as a string

        format: x_trackpad:trigger,trackpad_pressed, menuButton,grip_button
        essentially the pose has been cut ouf

        Returns:
            str: button state as string in the described format
        """
        x_trackpad = self._button_state["trackpad_x"]
        y_trackpad = self._button_state["trackpad_y"]
        trackpadPressed = self._button_state["trackpad_pressed"]
        triggerButton = self._button_state["trigger"]
        menuButton = self._button_state["menu_button"]
        gripButton = self._button_state["grip_button"]
        return x_trackpad+","+y_trackpad+":"+triggerButton+","+trackpadPressed+","+menuButton+","+gripButton

    def get_as_grpc_object(self) -> HandheldController:
        quat = Quaternion(quat=self.loc_rot)
        trans = self.loc_trans
        return HandheldController(ID=self.ID,
                                  rotation=quat,
                                  position=trans,
                                  button_state=self._button_state)


class Calibration():
    """representation of the calibration matrix which maps from virtual to tracker
    it saves this as a homogenous matrix which can be usd in processing

    Furthermore, a boolean is used to check if calibration has been set as this 
    is simply initialised with an empty calibration
    """

    def __init__(self):
        """initialise the matrix with the base homogenous matrix
        """
        temp_matrix = np.hstack([np.identity(n=3), np.zeros([3, 1])])
        temp_matrix = np.vstack([temp_matrix, np.array([0, 0, 0, 1])])
        self._calibration_matrix: np.ndarray = temp_matrix
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
        self._holo_tracker = None
        self._calibration_tracker = None
        self._controller = None
        self._controller_initialized = asyncio.Event()
        self._holo_tracker_initialized = asyncio.Event()
        self._calibration_tracker_initialized = asyncio.Event()
        self.calibration = Calibration()
        self._status: str = "no_status"
        self.new_state_subscriber: Dict[str, asyncio.Event] = dict()

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

    def init_holo_tracker(self, new_state: Tracker) -> None:

        logger.debug("Initing holo_tracker")
        self._holo_tracker = ViveTracker(ID=new_state.ID,
                                         location_rotation=new_state.rotation.quat,
                                         location_tranlation=new_state.position)
        self._holo_tracker_initialized.set()

    def init_calibration_tracker(self, new_state: Tracker) -> None:

        logger.debug("Initing calibration tracker")
        self._calibration_tracker = ViveTracker(ID=new_state.ID,
                                                location_rotation=new_state.rotation.quat,
                                                location_tranlation=new_state.position)
        self._calibration_tracker_initialized.set()

    def init_controller(self, new_state: HandheldController):
        logger.debug("Initing controller")
        self._controller = ViveController(ID=new_state.ID,
                                          location_rotation=new_state.rotation.quat,
                                          location_tranlation=new_state.position,
                                          button_state=new_state.button_state)
        logger.debug("Created object")
        self._controller_initialized.set()
