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

from backend_api.grpc_objects import (
    Tracker, Controller
)

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

    def poll(self) -> Tuple[List[Tracker], List[Controller]]:
        """ Poll the Lighthouse for each object
        if its found add its data to a dictionnary which is passed back
        """
        # TODO: Figure out how to find ID
        tracker_list = list()
        controller_list = list()
        logger.debug("Polling")
        """
        ----------
        Controller
        ----------
        """
        try:
            # get the position and rotation

            [x, y, z, w, i, j, k] = self.v.devices["controller_1"].get_pose_quaternion()
            # [x, y, z, w, i, j, k] = self.inject_calibration([x, y, z, w, i, j, k])
            # Now get the button states. An Example printed below
            # {'unPacketNum': 362, 'trigger': 0.0, 'trackpad_x': 0.0, 'trackpad_y': 0.0,
            # 'ulButtonPressed': 0, 'ulButtonTouched': 0, 'menu_button': False, 'trackpad_pressed': False, 'trackpad_touched': False, 'grip_button': False}
            button_state = self.v.devices["controller_1"].get_controller_inputs()
            # print(button_state)
            # turn trigger floating point value to boolean
            if button_state["trigger"] < 0.5:
                button_state["trigger"] = False
            else:
                button_state["trigger"] = True
            # turn all button states into string
            button_state = {key: str(value) for key, value in button_state.items()}

            controller_list.append(
                Controller(
                    name="mainController",
                    rotation=[i, j, k, w],
                    position=[x, y, z],
                    button_state=button_state)
            )
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
        TestController
        ----------
        """
        try:
            # get the position and rotation

            [x, y, z, w, i, j, k] = self.v.devices["handheld"].get_pose_quaternion()
            # [x, y, z, w, i, j, k] = self.inject_calibration([x, y, z, w, i, j, k])
            # Now get the button states. An Example printed below
            # {'unPacketNum': 362, 'trigger': 0.0, 'trackpad_x': 0.0, 'trackpad_y': 0.0,
            # 'ulButtonPressed': 0, 'ulButtonTouched': 0, 'menu_button': False, 'trackpad_pressed': False, 'trackpad_touched': False, 'grip_button': False}
            button_state = self.v.devices["handheld"].get_controller_inputs()
            # print(button_state)
            # turn trigger floating point value to boolean
            if button_state["trigger"] < 0.5:
                button_state["trigger"] = False
            else:
                button_state["trigger"] = True
            # turn all button states into string
            button_state = {key: str(value) for key, value in button_state.items()}

            controller_list.append(
                Controller(
                    name="testController",
                    rotation=[i, j, k, w],
                    position=[x, y, z],
                    button_state=button_state)
            )
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
            [x, y, z, w, i, j, k] = self.v.devices["holo_tracker"].get_pose_quaternion()
            tracker_list.append(Tracker(
                name="holoTracker",
                rotation=[i, j, k, w],
                position=[x, y, z],))
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
            [x, y, z, w, i, j, k] = self.v.devices["calibration_tracker"].get_pose_quaternion()
            tracker_list.append(Tracker(
                name="calibrationTracker",
                rotation=[i, j, k, w],
                position=[x, y, z],))
        except (TypeError, ZeroDivisionError):
            # this occurs when connection to device is lost
            # just use the previously detected pose
            # Zero divisoin error can happen during conversion to quaternion
            pass
        except KeyError as e:
            logger.warning(f"CalibrationTracker wasnt found: {e}")
        """
        ----------
        Robot
        ----------
        """
        # try:
        #     # get the position and rotation
        #     x, y, z = [1, 2, 3]
        #     i, j, k, w = [0, 0, 0, 1]
        #     tracker_list.append(Tracker(
        #         name="robot",
        #         rotation=[i, j, k, w],
        #         position=[x, y, z],))
        # except (TypeError, ZeroDivisionError):
        #     # this occurs when connection to device is lost
        #     # just use the previously detected pose
        #     # Zero divisoin error can happen during conversion to quaternion
        #     pass
        return tracker_list, controller_list

    def inject_calibration(self, data: List[float]) -> List[float]:
        # return data

        [x, y, z, w, i, j, k] = data

        """
        ----------
        Build homogenous matrix Controller->LH
        ----------
        """
        controller2LH_rot = R.from_quat([i, j, k, w])
        controller_pos_in_LH = np.array([x, y, z]).reshape([3, 1])
        hom_controller_2_LH = np.hstack([controller2LH_rot.as_matrix(), controller_pos_in_LH])
        hom_controller_2_LH = np.vstack([hom_controller_2_LH, np.array([0, 0, 0, 1])])
        """
        ----------
        Setting the calibration matrix. LH->virtual center manually
        ----------
        """
        s = """
        -0.89245719 -0.00868954 0.4510484 1.3099407
        -0.02266234 0.9994157 -0.0255864 -0.16905557
        -0.45056251 -0.03305658   -0.89213264 -1.11754632
        0.000000000000000000e+00 0.000000000000000000e+00 0.000000000000000000e+00 1.000000000000000000e+00
        """
        hom_LH_2_virtual_center = np.fromstring(s, dtype=float, sep=" ")
        hom_LH_2_virtual_center = hom_LH_2_virtual_center.reshape((4, 4))
        test_matrix = np.array([
            [-1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, -1, 0],
            [0, 0, 0, 1]
        ])
        test_matrix2 = np.array([
            [1, 0, 0, 0],
            [0, 0, -1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ])
        test_matrix3 = np.array([
            [-1, 0, 0, 0],
            [0, -1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        test_matrix4 = np.array([
            [-1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, -1, 0],
            [0, 0, 0, 1]
        ])
        """
        ----------
        Applying the transformation and extracting the rotation and transformation
        ----------
        """
        # hom_controller_2_LH[0, :] = -hom_controller_2_LH[0, :]
        # hom_controller_2_LH[:, 0] = -hom_controller_2_LH[:, 0]
        # @test_matrix3@test_matrix  # @test_matrix2
        # hom_controller_2_virtual_center = hom_LH_2_virtual_center@hom_controller_2_LH  @ test_matrix
        hom_controller_2_virtual_center = hom_controller_2_LH @ test_matrix
        logger.warning(f"no changes:\n {hom_controller_2_virtual_center}")

        # this is applied in holoCalibrator
        hom_controller_2_virtual_center[2, :] = -hom_controller_2_virtual_center[2, :]
        hom_controller_2_virtual_center[:, 2] = -hom_controller_2_virtual_center[:, 2]
        # logger.warning(f"z changed:\n {hom_controller_2_virtual_center}")
        # hom_controller_2_virtual_center[0, :] = -hom_controller_2_virtual_center[0, :]
        # hom_controller_2_virtual_center[:, 0] = -hom_controller_2_virtual_center[:, 0]
        # logger.warning(f"x changed: \n {hom_controller_2_virtual_center}")
        # hom_controller_2_virtual_center[0, :] = -hom_controller_2_virtual_center[0, :]
        # hom_controller_2_virtual_center[:, 0] = -hom_controller_2_virtual_center[:, 0]
        ###################################################
        target_rot = hom_controller_2_virtual_center[: 3, : 3]
        target_pos = hom_controller_2_virtual_center[: 3, 3]

        rot = R.from_matrix(target_rot)

        x, y, z = target_pos
        i, j, k, w = rot.as_quat()

        """
        ----------
        Convert to left hand KOS and change the quaternion scale to scalar first
        as to be in line with what would be expected of the lighthouse output
        ----------
        """

        # return [x-3.2, z, y+1.3+0.22, w, -i, -k, -j]
        # return x, y, -z, w, -i, -j, k
        return [x, y, z, w, i, j, k]
