"""This moduel finds the points to match against after being given a transformation
This moduel doesnt apply much logic just simply checks what points were chosen 
and then returns them in the correct 

There are 2 interfaces:
- get_points_real_object(vive_pos,vive_rot)
- get_points_virtual_object(unity_pos,unity_rot)

Both return a list of points on the object after being given a transformtion
the main difference lies in the fact that the  poitn of reference is on two different
position on the calibration object

Unity uses the cetner of the object as it was defined udirng the CAD while the 
LH Tracker uses its center. Hence, the point correspdonacnes need to eb etablished

Herein, we will define the points from the perspective of their relative coordinate origin.
For example we use the outer edge point of ht ebase hence we store this point as the first
in a two lists. Once for the Vive_orign and once for the unity origin

Each calibration object has its own class. Each with two functions. get_points_vive_ref and
get_points_unity_ref. They both return a nx3 matrix whic hcan be looped over to get the position 
in the base coordinate system
"""
from abc import ABC, abstractmethod
from typing import List, Union, Dict

from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R


class BaseCalibrationObject(ABC):
    @abstractmethod
    def get_points_vive_ref(self) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def get_points_unity_ref(self) -> np.ndarray:
        raise NotImplementedError


class FirstCalibrationObject(BaseCalibrationObject):
    """first prototype built.
    we take 16 points
    Front is defined as the location the viewer is facing the extra side wall directly.
    Starting lower base (the ground facing base):
    1. Point. left front 
    2. Point. right front
    3. Point right back 
    4. Point left back
    Middle base (there the incline begins)
    5. Point. left front
    6.->8. Point anti clockwise
    Upper Base
    9. Point left front
    10.->12. Point anti clockwise
    Center (along the center line)
    13. Point lower front center (ground facing )
    14. Point lower back center
    15. Point upper front center
    16. Point upper back center    
    """

    def get_points_unity_ref(self) -> np.ndarray:
        # the points we receive are in unity units which in standard settings are=1m
        # as the vive also works in meters we wont transform
        points = [
            [0.04, -0.015, -0.007],  # 1 Point
            [-0.04, -0.015, -0.007],
            [-0.04, 0.015, -0.007],
            [0.04, 0.015, -0.0070],
            [0.04, -0.015, 0.0213],   # 5 Point
            [-0.04, -0.015, 0.0213],
            [-0.04, 0.015, 0.0213],
            [0.04, 0.015, 0.0213],
            [0.015, -0.015, 0.051470],  # 9 Point
            [-0.015, -0.015, 0.05147],
            [-0.015, 0.015, 0.05147],
            [0.015, 0.015, 0.05147],
            [0, -0.015, -0.007],  # 13 Point
            [0, 0.015, -0.007],
            [0, -0.015, 0.051470],
            [0, 0.015, 0.05147],
        ]
        return np.array(points)

    def get_points_vive_ref(self) -> np.ndarray:
        """return calibration points inthe tracker frame. This uses the KOS
        as noted by the libsurvive team. The origin is assumed to be at the bore hole
        and flush with the ground

        Returns:
            np.ndarray: [description]
        """
        points = [
            [0.04, -0.02, 0.05217],  # 1 Point
            [-0.04, -0.02, 0.05217],
            [-0.04, 0.01, 0.05217],
            [0.04, 0.01, 0.05217],
            [0.04, -0.02, 0.03017],  # 5 Point
            [-0.04, -0.02, 0.030170],
            [-0.04, 0.01, 0.030170],
            [0.04, 0.01, 0.030170],
            [0.015, -0.02, 0],  # 9 Point
            [-0.015, -0.02, 0],
            [-0.015, 0.01, 0],
            [0.015, 0.01, 0],
            [0, -0.02, 0.052170],  # 13 Point
            [0, 0.01, 0.052170],
            [0, -0.02, 0],
            [0, 0.01, 0],
        ]
        return np.array(points)


def _get_active_calibration_object() -> Union[FirstCalibrationObject]:
    from config.api import CalibrationObject
    from config.const import CALIBRATION_OBJECT
    lookup_table: Dict[CalibrationObject, Union[FirstCalibrationObject]] = {
        CalibrationObject.FIRSTPROTOTYPE: FirstCalibrationObject()
    }
    return lookup_table[CALIBRATION_OBJECT]


def get_points_tracker_kos(hom_matrix: np.ndarray) -> List[np.ndarray]:
    calib_obj = FirstCalibrationObject()
    points = calib_obj.get_points_vive_ref()
    points_in_lh = list()
    for p in points:
        p_aug = np.append(p, [1])
        points_in_lh.append(hom_matrix@p_aug)
    return points_in_lh


def get_points_unity_kos(hom_matrix: np.ndarray) -> List[np.ndarray]:
    calib_obj = FirstCalibrationObject()
    points = calib_obj.get_points_unity_ref()
    points_in_unity = list()
    for p in points:
        p_aug = np.append(p, [1])
        points_in_unity.append(hom_matrix@p_aug)
    return points_in_unity
