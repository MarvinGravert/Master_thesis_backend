from typing import Any, Dict, List, Union
import asyncio
from enum import Enum

from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R

from holoViveCom_pb2 import CalibrationInfo, Tracker, Quaternion, HandheldController


class VRObject():
    def __init__(self,
                 position: List[float],
                 rotation: List[float],
                 ) -> None:
        self.position = position  # x y z
        self.rotation = rotation  # w i j k

    def get_pose_as_hom_matrix(self) -> np.ndarray:
        """returns the current pose (postion+quat) as a 4x4 homogenous matrix

        Returns:
            np.ndarray: 4x4 homogenous matrix
        """
        w, i, j, k = self.rotation
        rot = R.from_quat([i, j, k, w])  # scipy wants scalar last)
        rot_matrix = rot.as_matrix()
        hom_matrix = np.hstack([rot_matrix, np.array(self.position).reshape([3, 1])])
        return np.vstack([hom_matrix, [0, 0, 0, 1]])

    def get_pose_as_float_array(self) -> List[float]:
        """returns position and rotation quaternion as a list of floats 

        Returns:
            list (float): Format: x y z w i j k"""
        return [*self.position, *self.rotation]

    @classmethod
    def set_pose_via_grpc_object(cls, grpc_object: Union[Tracker, HandheldController]):
        position = grpc_object.position
        rotation = grpc_object.rotation.quat

        return cls(position=position, rotation=rotation)


class ViveTracker(VRObject):

    def get_as_grpc_object(self) -> Tracker:
        quat = Quaternion(quat=self.rotation)
        trans = self.position
        return Tracker(rotation=quat, position=trans)


class Calibration():
    """class to hold the calibration matrices which are necessary to output
    the waypoint in the desired coordinate system. These are LH->virtual center
    and LH->Robot
    """

    def __init__(self):
        """init the matrices from strings to make it easier to copy paste new calibration info
        at the moment only the LH->virtual center may be changed automatically by the services
        """
        LH_2_virtual = """
        1 0 0 0
        0 1 0 0
        0 0 1 0
        0 0 0 1
        """

        self._LH_2_virtual_matrix: np.ndarray = np.fromstring(LH_2_virtual,
                                                              dtype=float,
                                                              sep=" ").reshape((4, 4))

        LH_2_robot = """
        1 0 0 0
        0 1 0 0
        0 0 1 0
        0 0 0 1
        """
        self._LH_2_robot_matrix: np.ndarray = np.fromstring(LH_2_robot,
                                                            dtype=float,
                                                            sep=" ").reshape((4, 4))

    @property
    def LH_2_virtual_matrix(self) -> np.ndarray:
        return self._LH_2_virtual_matrix

    @property
    def LH_2_robot_matrix(self) -> np.ndarray:
        return self._LH_2_robot_matrix

    def set_holo_calibration_via_grpc_object(self, calibration_info: CalibrationInfo) -> None:
        """setting the calibration matrix when handed via gprc_object

        the object is a flattend 4x4 matrix

        Args:
            calibration_info (CalibrationInfo): [description]
        """
        flattend_matrix: np.ndarray = calibration_info.calibrationMatrixRowMajor
        self._LH_2_virtual_matrix = flattend_matrix.reshape([4, 4])
        logger.debug(f"New calibration has been set to: \n {self.calibration_matrix}")


class VRState():
    def __init__(self):
        self._holo_tracker = None
        self._controller = None
        self.calibration = Calibration()

    @ property
    def holo_tracker(self) -> ViveTracker:
        return self._holo_tracker

    @ holo_tracker.setter
    def holo_tracker(self, new_tracker: ViveTracker):
        self._holo_tracker = new_tracker

    @ property
    def controller(self) -> VRObject:
        return self._controller

    @ controller.setter
    def calibration_tracker(self, new_controller: VRObject):
        self._controller = new_controller


class IncorrectMessageFormat(Exception):
    pass
