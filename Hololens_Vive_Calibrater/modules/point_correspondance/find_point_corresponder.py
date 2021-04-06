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
            [-0.04, 0.015, -0.007],  # 1 Point
            [0.04, 0.015, -0.007],
            [0.04, -0.015, -0.007],
            [-0.04, -0.015, -0.0070],
            [-0.04, 0.015, 0.0213],   # 5 Point
            [0.04, 0.015, 0.0213],
            [0.04, -0.015, 0.0213],
            [-0.04, -0.015, 0.0213],
            [-0.015, 0.015, 0.051470],  # 9 Point
            [0.015, 0.015, 0.05147],
            [0.015, -0.015, 0.05147],
            [-0.015, -0.015, 0.05147],
            [0, 0.015, -0.007],  # 13 Point
            [0, -0.015, -0.007],
            [0, 0.015, 0.051470],
            [0, -0.015, 0.05147],
        ]
        # swap axis y and z
        points = np.array(points)
        # points[:, [1, 2]] = points[:, [2, 1]]
        # points = [
        #     [-0.04, 0.015, 0.007],  # 1 Point
        #     [0.04, 0.015, 0.007],
        #     [0.04, -0.015, 0.007],
        #     [-0.04, -0.015, 0.0070],
        #     [-0.04, 0.015, -0.0213],   # 5 Point
        #     [0.04, 0.015, -0.0213],
        #     [0.04, -0.015, -0.0213],
        #     [-0.04, -0.015, -0.0213],
        #     [-0.015, 0.015, -0.051470],  # 9 Point
        #     [0.015, 0.015, -0.05147],
        #     [0.015, -0.015, -0.05147],
        #     [-0.015, -0.015, -0.05147],
        #     [0, 0.015, 0.007],  # 13 Point
        #     [0, -0.015, 0.007],
        #     [0, 0.015, -0.051470],
        #     [0, -0.015, -0.05147],
        # ]
        return points

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


def get_points_real_object(vive_trans: List[float], vive_rot: List[float]) -> np.ndarray:
    # triad sends the position as w i j k (scalar first)
    # rotation wants it scalar last
    logger.debug("Starting points acquisition for vive calibration object")
    logger.debug(f"The vive position: {vive_trans} \n and the vive rotation:{vive_rot}")
    w, i, j, k = vive_rot
    rot_matrix: R = R.from_quat([i, j, k, w])
    hom_matrix = np.hstack([
        rot_matrix.as_matrix(),
        np.array(vive_trans).reshape([3, 1])
    ])  # reshape just to be safe
    hom_matrix = np.vstack([hom_matrix, [0, 0, 0, 1]])
    # now run over all points and rotate them by the matrix=>give us all points in the
    # LH coordinate frame
    transformed_points = list()
    cali_object = _get_active_calibration_object()
    for point in cali_object.get_points_vive_ref():
        # concat the retrieved point to make it align with the homogenous matrix
        transformed_points.append(hom_matrix@np.concatenate([point, [1]]))
    # cut away the homogenous part
    return np.array(transformed_points)[:, :3]


def get_points_virtual_object_old(unity_trans: List[float], unity_rot: List[float]) -> np.ndarray:
    """returns for a given pose (position+rotation) the points of the calibration object
    in reference to the reference used in unity (depends on the rotation+translation handed)

    the received transformation (it shuold be from cali-object-KOS->reference in hololens world)
    is first used to contruct a homogenous matrix.
    Then this is used to calculate the calibration points in the reference KOS
    Finally, the left hand KOS is transformed to a right hand KOS before returning

    Args:
        unity_trans (List[float]): position of unity 
        unity_rot ([type]): [description]

    Returns:
        np.ndarray: [description]
    """
    # unity transmits i j k w and as rotation want the scalar last its all good
    logger.debug("Starting points acquisition for unity calibration object")
    x, y, z = unity_trans
    # unity_trans=[x,z,y]
    i, j, k, w = unity_rot
    # rot_matrix: R = R.from_quat([-i,-j,-k,w])
    rot_matrix: R = R.from_quat(unity_rot)
    hom_matrix = np.hstack([
        rot_matrix.as_matrix(),
        np.array(unity_trans).reshape([3, 1])
    ])  # reshape just to be safe
    hom_matrix = np.vstack([hom_matrix, [0, 0, 0, 1]])
    ###########################
    hom_matrix[2, :] = -hom_matrix[2, :]
    hom_matrix[:, 2] = -hom_matrix[:, 2]
    ############################
    # now run over all points and rotate them by the matrix=>give us all points in the
    # unity base frame

    transformed_points = list()
    cali_object = _get_active_calibration_object()
    for point in cali_object.get_points_unity_ref():
        # concat the retrieved point to make it align with the homogenous matrix
        transformed_points.append(hom_matrix@np.concatenate([point,  [1]]))
    # cut away the homogenous part
    # just right for the transformation
    transformed_points = np.array(transformed_points)[:, :3]
    logger.debug("Converting to RH KOS")
    # transformed_points = [_convert_left_to_right_hand_kos(
    #     position) for position in transformed_points]
    return np.array(transformed_points)


def get_points_virtual_object(unity_trans: List[float], unity_rot: List[float]) -> np.ndarray:
    """returns for a given pose (position+rotation) the points of the calibration object
    in reference to the reference used in unity (depends on the rotation+translation handed)

    the received transformation (it shuold be from cali-object-KOS->reference in hololens world)
    is first used to contruct a homogenous matrix.
    Then this is used to calculate the calibration points in the reference KOS
    Finally, the left hand KOS is transformed to a right hand KOS before returning

    Args:
        unity_trans (List[float]): position of unity 
        unity_rot ([type]): [description]

    Returns:
        np.ndarray: [description]
    """
    # unity transmits i j k w and as rotation want the scalar last its all good
    logger.debug("Starting points acquisition for unity calibration object")
    x, y, z = unity_trans
    i, j, k, w = unity_rot
    rot_matrix: R = R.from_quat(unity_rot)
    hom_matrix = np.hstack([
        rot_matrix.as_matrix(),
        np.array(unity_trans).reshape([3, 1])
    ])  # reshape just to be safe
    # rot_matrix: R = R.from_quat([-i, -k, -j, w])
    # hom_matrix = np.hstack([
    #     rot_matrix.as_matrix(),
    #     np.array([x, z, y]).reshape([3, 1])
    # ])  # reshape just to be safe
    hom_matrix = np.vstack([hom_matrix, [0, 0, 0, 1]])
    ############################
    # now run over all points and rotate them by the matrix=>give us all points in the
    # unity base frame

    transformed_points = list()
    cali_object = _get_active_calibration_object()
    for point in cali_object.get_points_unity_ref():
        # concat the retrieved point to make it align with the homogenous matrix
        transformed_points.append(hom_matrix@np.concatenate([point,  [1]]))
    # cut away the homogenous part
    # just right for the transformation
    transformed_points = np.array(transformed_points)[:, :3]
    logger.debug("Converting to RH KOS")
    transformed_points = [_convert_left_to_right_hand_kos(
        position) for position in transformed_points]
    return np.array(transformed_points)


def _convert_left_to_right_hand_kos(pos: np.ndarray) -> np.ndarray:
    # we need to convert to a right hand kos before we can process the unity
    # object position
    # exchange y and z

    position = np.array([pos[0], pos[2], pos[1]])

    # # negate the angles keep the sclar and swap j k
    # rotation = np.array([
    #     -rot[0],
    #     -rot[2],
    #     -rot[1],
    #     rot[3]])

    return position


if __name__ == "__main__":
    t = get_points_virtual_object(unity_rot=[1, 0, 0, 1], unity_trans=[10, 20, 30])
    print(t)
    c = get_points_real_object(vive_rot=[1, 0, 0, 1], vive_trans=[10, 20, 30])
    print(c)
