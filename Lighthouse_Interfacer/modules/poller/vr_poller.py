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

from backend_api.vr_objects import VRObject, ViveController, ViveTracker

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

            [x, y, z, w, i, j, k] = self.v.devices["handheld"].get_pose_quaternion()
            [x, y, z, w, i, j, k] = self.inject_calibration([x, y, z, w, i, j, k])
            # Now get the button states. An Example printed below
            # {'unPacketNum': 362, 'trigger': 0.0, 'trackpad_x': 0.0, 'trackpad_y': 0.0,
            # 'ulButtonPressed': 0, 'ulButtonTouched': 0, 'menu_button': False, 'trackpad_pressed': False, 'trackpad_touched': False, 'grip_button': False}
            button_state = self.v.devices["handheld"].get_controller_inputs()
            # turn all button states into string
            button_state = {key: str(value) for key, value in button_state.items()}

            state_dict["controller"] = ViveController(
                rotation=[w, i, j, k],
                position=[x, y, z],
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
            [x, y, z, w, i, j, k] = self.v.devices["holo_tracker"].get_pose_quaternion()
            state_dict["holo_tracker"] = ViveTracker(
                rotation=[w, i, j, k],
                poosition=[x, y, z],).get_as_grpc_object()
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
            state_dict["calibration_tracker"] = ViveTracker(
                rotation=[w, i, j, k],
                position=[x, y, z],).get_as_grpc_object()
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
        # wor = w
        # ior = i
        # jor = j
        # kor = k
        # R = np.array([
        #     [-1, 9.979074001312255859e-01, -6.458293646574020386e-02],
        #     [9.871731996536254883e-01, 1, 5.138471350073814392e-02],
        #     [2.500897049903869629e-01, 3.596465336158871651e-03, -1]
        # ])

        # x, y, z = R@np.array([x, y, z])+[5.620775818824768066e-01,
        #                                  2.334415316581726074e-01, -2.949469089508056641e+00]

        # return [x-1.2, y, -z-0.33, w, i, -j, -k]
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
        4.995881915092468262e-01 -3.909247927367687225e-03 8.662542104721069336e-01 6.140581965446472168e-01
        8.662549257278442383e-01 6.575234234333038330e-03 -4.995589554309844971e-01 -1.447103857994079590e+00
        -3.742924425750970840e-03 9.999707341194152832e-01 6.671314593404531479e-03 2.097773104906082153e-01
        0.000000000000000000e+00 0.000000000000000000e+00 0.000000000000000000e+00 1.000000000000000000e+00
        """
        hom_LH_2_virtual_center = np.fromstring(s, dtype=float, sep=" ")
        hom_LH_2_virtual_center = hom_LH_2_virtual_center.reshape((4, 4))
        test_matrix = np.array([
            [1, 0, 0, 0],
            [0, 0, -1, 0],
            [0, 1, 0, 0],
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
        hom_controller_2_virtual_center = hom_LH_2_virtual_center@test_matrix4@hom_controller_2_LH@test_matrix3@test_matrix  # @test_matrix2
        # hom_controller_2_virtual_center = test_matrix@hom_controller_2_LH

        # hom_controller_2_virtual_center[2,:]=-hom_controller_2_virtual_center[2,:]
        # hom_controller_2_virtual_center[:,2]=-hom_controller_2_virtual_center[:,2]

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

        return [x-3.2, z, y+1.3+0.22, w, -i, -k, -j]
        # return [x, y, z, w, i, j, k]
