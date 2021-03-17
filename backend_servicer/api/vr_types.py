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
        self._last_state_menu_button = False
        self._button_state = self._check_and_adjust_button_states(button_state)

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
