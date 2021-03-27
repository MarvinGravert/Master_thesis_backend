from typing import Tuple, Union, List
from scipy.spatial.transform import Rotation as R
import numpy as np


def combine_to_homogeneous_matrix(
        rotation_matrix: np.ndarray, translation_vector: np.ndarray) -> np.ndarray:
    """combine rotation matrix and translation vector together to create a 4x4
    homgeneous matrix

    Args:
        rotation_matrix (np.ndarray): 3x3 matrix
        translation_vector (np.ndarray): 3x1 or (3,) vector

    Returns:
        np.ndarray: 4x4 homogeneous matrix
    """
    temp = np.hstack((rotation_matrix, translation_vector.reshape((-1, 1))))
    return np.vstack((temp, [0, 0, 0, 1]))


def separate_from_homogeneous_matrix(homogenous_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """separate the rotation matrix and translation vector from the homogenous matrix

    Args:
        homogenous_matrix (np.ndarray): 4x4 homogenous matrix

    Returns:
        Tuple[np.ndarray, np.ndarray]: 3x3 rotation matrix, (3,1) rotation vector
    """
    return homogenous_matrix[:3, :3], homogenous_matrix[:3, 3]


def extract_position_and_quaternion_from_homogeneous_matrix(
        homogenous_matrix: np.ndarray) -> Tuple[
        np.ndarray, np.ndarray]:
    """extract position and quaternion representation from a 4x4 homogeneous matrix

    Args:
        homogenous_matrix (np.ndarray): 4x4 homogeneous

    Returns:
        Tuple[np.ndarray, np.ndarray]: (3,)position, (4,) quaternion i j k w
    """
    r, t = separate_from_homogeneous_matrix(homogenous_matrix)
    quat = R.from_matrix(r).as_quat()
    return t, quat


def transform_to_homogenous_matrix(
    position: Union[np.ndarray, List[float]],
    quaternion: Union[np.ndarray, List[float]],
    scalar_first: bool = False
) -> np.ndarray:
    """given a position and a quaternion calculates the homogeneous representation

    Args:
        position (Union[np.ndarray, List[float]]): x y z position
        quaternion (Union[np.ndarray, List[float]]): quaternion i j k w
        scalar_first (bool): use w i j k instead
    Returns:
        np.ndarray: 4x4 homogeneous matrix
    """
    if scalar_first:
        w, i, j, k = quaternion
        quaternion = [i, j, k, w]
    r = R.from_quat(quaternion)
    p = np.array(position).reshape((-1, 1))
    temp = np.hstack((r.as_matrix(), p))
    return np.vstack((temp, [0, 0, 0, 1]))
