"""This module is gonna poll include the polling interface to the vive
it polls on a certain frequency and then pushes into a grpc interface

Multiple Exceptions are handeled herein:
-no connection to openvr => openvr.error_code.InitError_Init_PathRegistryNotFound
-no device found
    """
import time
from typing import Dict, Any, List, Tuple

from loguru import logger
from openvr.error_code import InitError_Init_PathRegistryNotFound, InitError_Init_HmdNotFoundPresenceFailed
import numpy as np
from scipy.spatial.transform import Rotation as R

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
        except InitError_Init_HmdNotFoundPresenceFailed:
            logger.error("No HMD Found. Forgot to set null driver probably")
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
            [x, y, z, w, i, j, k] = self.inject_calibration([x, y, z, w, i, j, k])
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
        except (TypeError, ZeroDivisionError) as e:
            # this occurs when connection to device is lost
            # just use the previously detected pose
            # Zero divisoin error can happen during conversion to quaternion
            logger.error(e)
            pass
        except KeyError as e:
            logger.warning(f"Controller wasnt found: {e}")

        """
        ----------
        Holo Tracker
        ----------
        """
        try:
            # get the position and rotation
            [x, y, z, i, j, k, w] = self.v.devices["holo_tracker"].get_pose_quaternion()
            state_dict["holo_tracker"] = ViveTracker(
                ID="holotracker",
                location_rotation=[w, i, j, k],
                location_tranlation=[x, y, z],).get_as_grpc_object()
        except (TypeError, ZeroDivisionError):
            # this occurs when connection to device is lost
            # just use the previously detected pose
            # Zero divisoin error can happen during conversion to quaternion
            pass
        except KeyError as e:
            logger.warning(f"HoloTracker wasnt found: {e}")
        """
        ----------
        Calibration Tracker
        ----------
        """
        try:
            # get the position and rotation
            [x, y, z, i, j, k, w] = self.v.devices["calibration_tracker"].get_pose_quaternion()
            state_dict["calibration_tracker"] = ViveTracker(
                ID="calibration_tracker",
                location_rotation=[w, i, j, k],
                location_tranlation=[x, y, z],).get_as_grpc_object()
        except (TypeError, ZeroDivisionError):
            # this occurs when connection to device is lost
            # just use the previously detected pose
            # Zero divisoin error can happen during conversion to quaternion
            pass
        except KeyError as e:
            logger.warning(f"CalibrationTracker wasnt found: {e}")
        return state_dict

    def inject_calibration(self, data: List[float]) -> List[float]:
        # return data

        [x, y, z, w, i, j, k] = data

        controller2LH_rot = R.from_quat([i, j, k, w])
        controller_pos_in_LH = np.array([x, y, z]).reshape([3, 1])
        hom_controller_2_LH = np.hstack([controller2LH_rot.as_matrix(), controller_pos_in_LH])
        hom_controller_2_LH = np.vstack([hom_controller_2_LH, np.array([0, 0, 0, 1])])

        hom_LH_2_virtual_center = np.array([
            [1, 2, 3, 9],
            [2, 3, 4, 19],
            [3, 3, 2, 20],
            [0, 0, 0, 1]
        ])

        hom_controller_2_virtual_center = hom_LH_2_virtual_center@hom_controller_2_LH

        target_rot = hom_controller_2_virtual_center[:3, :3]
        target_pos = hom_controller_2_virtual_center[:3, 3]

        rot = R.from_matrix(target_rot)

        x, y, z = target_pos
        i, j, k, w = rot.as_quat()

        # convert to left hand and scal

        return [x, z, y, w, -i, -k, -j]
