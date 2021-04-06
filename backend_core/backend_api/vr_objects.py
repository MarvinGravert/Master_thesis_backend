from typing import Dict, List, Union

from loguru import logger
from scipy.spatial.transform import Rotation as R, rotation
import numpy as np

from holoViveCom_pb2 import (
    HandheldController,  Quaternion, Tracker
)
from backend_utils.linear_algebra_helper import transform_to_homogenous_matrix


class VRObject():
    def __init__(self,
                 position: List[float],
                 rotation: List[float]) -> None:

        self.rotation = rotation  # w i j k
        self.position = position  # x y z

    def get_pose_as_hom_matrix(self) -> np.ndarray:
        """returns the current pose (postion+quat) as a 4x4 homogenous matrix

        Returns:
            np.ndarray: 4x4 homogenous matrix
        """
        return transform_to_homogenous_matrix(position=self.position,
                                              quaternion=self.rotation,
                                              scalar_first=True)

    def get_pose_as_float_array(self) -> List[float]:
        # x y z w i j k
        return [*self.position, *self.rotation]

    @classmethod
    def set_pose_via_grpc_object(cls,
                                 grpc_object: Union[Tracker, HandheldController]):
        position = grpc_object.position
        rotation = grpc_object.rotation.quat

        return cls(position=position, rotation=rotation)


class ViveTracker(VRObject):
    def update_state(self, new_data: Tracker):
        self.rotation = new_data.rotation.quat
        self.position = new_data.position

    def get_as_grpc_object(self) -> Tracker:
        quat = Quaternion(quat=self.rotation)
        return Tracker(rotation=quat, position=self.position)


class ViveController(VRObject):
    def __init__(self,
                 position: List[float],
                 rotation: List[float],
                 button_state: Dict[str, str]) -> None:
        super().__init__(position=position, rotation=rotation)
        self._last_state_menu_button = "False"
        self.menu_button_pressed_down = False
        self._button_state = button_state

    def update_state(self, new_data: HandheldController):
        """updates the internal state of the controller and runs checks on the buttons

        Args:
            new_data (HandheldController): grpc object containing the new data
        """
        self.rotation = new_data.rotation.quat
        self.position = new_data.position
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

        if self._last_state_menu_button == "False" and \
                button_state["menu_button"] == "True":
            self.menu_button_pressed_down = True

        self._last_state_menu_button = button_state["menu_button"]
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

        s = ",".join([str(i) for i in self.position])+":"
        s += ",".join([str(i) for i in self.rotation])+":"

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
        quat = Quaternion(quat=self.rotation)
        position = self.position
        return HandheldController(
            rotation=quat,
            position=position,
            button_state=self._button_state)
