"""This module is gonna poll include the polling interface to the vive
it polls on a certain frequency and then pushes into a grpc interface

Multiple Exceptions are handeled herein:
-no connection to openvr => openvr.error_code.InitError_Init_PathRegistryNotFound
-no device found
    """
import time
from typing import Dict, Any

from loguru import logger
from openvr.error_code import InitError_Init_PathRegistryNotFound

from config.api_types import VRObject, ViveController, ViveTracker
from utils.triad_openvr import triad_openvr  # file from triad Repo
from modules.poller.base_poller import BasePoller
from config.api_types import (
    OpenVRConnectionError
)


class VRPoller(BasePoller):
    def __init__(self, config_file_path=None) -> None:
        self._last_time = time.time()
        self._config_file_path = config_file_path  # Path to the setup file

    def start(self) -> None:
        try:
            self.v = triad_openvr(configfile_path=self._config_file_path)

            logger.info(self.v.print_discovered_objects())
        except InitError_Init_PathRegistryNotFound:
            logger.error("No connection to OpenVR")
            raise OpenVRConnectionError

    def poll(self) -> Dict[str, Any]:
        """ Poll the Lighthouse for each object
        if its found add its data to a dictionnary which is passed back
        """
        # TODO: Figure out how to find ID
        state_dict = dict()
        logger.debug("Polling")
        """
        ----------
        Controller
        ----------
        """
        try:
            # get the position and rotation

            [x, y, z, w, i, j, k] = self.v.devices["controller_1"].get_pose_quaternion()

            # Now get the button states. An Example printed below
            # {'unPacketNum': 362, 'trigger': 0.0, 'trackpad_x': 0.0, 'trackpad_y': 0.0,
            # 'ulButtonPressed': 0, 'ulButtonTouched': 0, 'menu_button': False, 'trackpad_pressed': False, 'trackpad_touched': False, 'grip_button': False}
            button_state = self.v.devices["controller_1"].get_controller_inputs()
            # turn all button states into string
            button_state = {key: str(value) for key, value in button_state.items()}
            state_dict["controller"] = ViveController(
                ID="controller",
                location_rotation=[w, i, j, k],
                location_tranlation=[x, y, z],
                button_state=button_state).get_as_grpc_object()
        # except (TypeError, ZeroDivisionError) as e:
        #     # this occurs when connection to device is lost
        #     # just use the previously detected pose
        #     # Zero divisoin error can happen during conversion to quaternion
        #     logger.error(e)
        #     pass
        except Exception as e:
            logger.error(e)

        """
        ----------
        Holo Tracker
        ----------
        """
        # try:
        #     # get the position and rotation
        #     [x, y, z, i, j, k, w] = self.v.devices["tracker_1"].get_pose_quaternion()
        #     state_dict["holo_tracker"] = ViveTracker(
        #         ID="holotracker",
        #         location_rotation=[w, i, j, k],
        #         location_tranlation=[x, y, z],).get_as_grpc_object()
        # except (TypeError, ZeroDivisionError):
        #     # this occurs when connection to device is lost
        #     # just use the previously detected pose
        #     # Zero divisoin error can happen during conversion to quaternion
        #     pass
        # """
        # ----------
        # Calibration Tracker
        # ----------
        # """
        # try:
        #     # get the position and rotation
        #     [x, y, z, i, j, k, w] = self.v.devices["tracker_2"].get_pose_quaternion()
        #     state_dict["calibration_tracker"] = ViveTracker(
        #         ID="calibration_tracker",
        #         location_rotation=[w, i, j, k],
        #         location_tranlation=[x, y, z],).get_as_grpc_object()
        # except (TypeError, ZeroDivisionError):
        #     # this occurs when connection to device is lost
        #     # just use the previously detected pose
        #     # Zero divisoin error can happen during conversion to quaternion
        #     pass

        return state_dict
