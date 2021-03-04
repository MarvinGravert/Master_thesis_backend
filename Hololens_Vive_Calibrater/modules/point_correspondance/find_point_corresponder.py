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
from typing import List

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
    Starting lower base:
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
    13. Point lower front center
    14. Point lower front center
    15. Point upper front center
    16. Point upper back center    
    """

    def get_points_unity_ref(self) -> np.ndarray:
        points = [
            [1, 0, 0],  # 1 Point
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],  # 5 Point
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],  # 9 Point
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],  # 13 Point
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
        ]
        return np.array(points)

    def get_points_vive_ref(self) -> np.ndarray:
        points = [
            [1, 0, 0],  # 1 Point
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],  # 5 Point
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],  # 9 Point
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],  # 13 Point
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
        ]
        return np.array(points)


def get_points_real_object(vive_trans: np.ndarray, vive_rot: np.ndarray) -> np.ndarray:
    # triad sends the position as w i j k (scalar first)
    # rotation wants it scalar last
    w, i, j, k = vive_rot
    rot_matrix: R = R.from_quat([i, j, k, w])
    hom_matrix = np.hstack([
        rot_matrix.as_matrix(),
        vive_trans.reshape([3, 1])
    ])  # reshape just to be safe
    hom_matrix = np.vstack([hom_matrix, [0, 0, 0, 1]])
    # now run over all points and rotate them by the matrix=>give us all points in the
    # LH coordinate frame
    transformed_points = list()
    cali_object = FirstCalibrationObject()
    for point in cali_object.get_points_vive_ref():
        transformed_points.append(hom_matrix@point)
    return np.ndarray(transformed_points)


def get_points_virtual_object(unity_trans, unity_rot) -> np.ndarray:
    # unity transmits i j k w
    # just right for the transformation
    position, rotation = _convert_left_to_right_hand_kos(unity_trans, unity_rot)
    rot_matrix: R = R.from_quat(rotation)
    hom_matrix = np.hstack([
        rot_matrix.as_matrix(),
        position.reshape([3, 1])
    ])  # reshape just to be safe
    hom_matrix = np.vstack([hom_matrix, [0, 0, 0, 1]])
    # now run over all points and rotate them by the matrix=>give us all points in the
    # unity base frame
    transformed_points = list()
    cali_object = FirstCalibrationObject()
    for point in cali_object.get_points_unity_ref():
        transformed_points.append(hom_matrix@point)
    return np.ndarray(transformed_points)


def _convert_left_to_right_hand_kos(pos: np.ndarray, rot: np.ndarray) -> List[np.ndarray]:
    # we need to convert to a right hand kos before we can process the unity
    # object position
    # exchange y and z
    logger.debug("Converting to RH KOS")
    position = np.array([pos[0], pos[2], pos[1]])
    # negate the angles keep the sclar and swap j k
    rotation = np.array([
        -rot[0],
        -rot[2],
        -rot[1],
        rot[3]])

    return [position, rotation]
