from typing import Any, Dict, List
import asyncio
from enum import Enum
from dataclasses import dataclass, fields
from backend_utils.linear_algebra_helper import transform_to_homogenous_matrix

from loguru import logger
from scipy.spatial.transform import Rotation as R, rotation
import numpy as np


class Calibration():
    """class to hold the calibration matrices (e.g. LH to robot and LH to virtual center)
    """

    def __init__(self, calibration_matrix: str =
                 """
                1 0 0 0
                0 1 0 0
                0 0 1 0
                0 0 0 1
                """):
        """init the matrices from strings to make it easier to copy paste new calibration info
        This was done to easier copy and paste calibration matrices from text during debugging
        """
        LH_2_virtual = calibration_matrix

        self._matrix: np.ndarray = np.fromstring(LH_2_virtual,
                                                 dtype=float,
                                                 sep=" ").reshape((4, 4))

    @ property
    def matrix(self) -> np.ndarray:
        return self._matrix


class InterpolationType(Enum):
    Linear = "Linear"
    PTP = "PTP"


@dataclass
class Waypoint():
    position: np.ndarray
    rotation: np.ndarray
    type: InterpolationType

    def apply_offset(self, offset: np.ndarray):
        # the location of the waypoint is in gernal not at the origin of the controller kos
        # thus it the point of reference has to be moved in its local kos
        # the rotation is unaffected
        # offset shuold be the vector from controller origin to waypoint reference position
        r = R.from_quat(self.rotation)
        # t=R@offset+t
        # Need to transform the local point into lighthouse-kos and then add to already existing position
        self.position = self.position+r.as_matrix()@offset

    def as_hom_matrix(self):

        return transform_to_homogenous_matrix(position=self.position, quaternion=self.rotation)
