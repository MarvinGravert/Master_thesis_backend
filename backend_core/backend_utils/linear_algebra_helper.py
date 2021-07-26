from typing import Tuple, Union, List
from numpy.core.numeric import empty_like
from numpy.core.shape_base import hstack
from numpy.lib.function_base import append
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


def calc_reprojection_error(
    point_set_a: np.ndarray,
    point_set_b: np.ndarray,
    hom_matrix: np.ndarray
) -> Tuple[float]:
    """calculates the reprojection error of a transformation between two point
    sets

    a={a_i}, b={b_i}
    e_i=||b_i-T*a_i|| # T:4x4 hom matrix
    RMSE: e = sqrt(sum(e_i**2)/num_points)
    MAE: e = sum(e_i)/num_points #mittlerer absoluter Fehler

    Args:
        point_set_a (np.ndarray): nx3 or nx4 matrix of points
        point_set_b (np.ndarray): nx3 or nx4 mastrix of points
        hom_matrix (np.ndarray): 4x4 homogenous matrix mapping from a->b

    Returns:
        Tuple[float,float]: root mean square error, mean average error
    """
    num_points = point_set_a.shape[0]
    # First check and possible augment
    if point_set_a.shape[1] == 3:
        ones = np.ones((num_points, 1))
        point_set_a = np.hstack((point_set_a, ones))
        point_set_b = np.hstack((point_set_b, ones))

    # lets do it weirdly just to be sure numpy is doing it correclty
    error = np.empty_like(point_set_a)
    for i in range(num_points):
        error[i, :] = point_set_b[i, :]-hom_matrix@point_set_a[i, :]

    # cut augmented column
    error = error[:, :3]
    sum_squared_error = 0
    sum_error = 0
    err_list = list()
    for i in range(num_points):
        err_mag = np.linalg.norm(error[i, :3])
        err_list.append(err_mag)
        sum_error += err_mag
        sum_squared_error += err_mag**2

    std = np.std(err_list)

    rmse = np.sqrt(sum_squared_error/num_points)
    mae = sum_error/num_points
    return rmse, mae, std


def single_reprojection_error(point_a, point_b, hom_matrix) -> float:
    """calculates the reprojection error for given hom matrix between
    two points correspodnance

    Args:
        point_set_a (np.ndarray): 1x3 or 1x4 point
        point_set_b (np.ndarray): 1x3 or 1x4 mastrix of points
        hom_matrix (np.ndarray): 4x4 homogenous matrix mapping from a->b

    Returns:
        float: error
    """
    if point_a.shape[1] == 3:
        ones = np.ones((1, 1))
        point_a = np.hstack((point_a, ones))
        point_b = np.hstack((point_b, ones))

    error = point_b-hom_matrix@point_a

    return np.linalg.norm(error)


def reprojection_error_axis_depending(point_set_a: np.ndarray,
                                      point_set_b: np.ndarray,
                                      hom_matrix: np.ndarray):
    """calculate the reprojection error in the axis of the target system

    Returns the rmse and mae axis depening (aka 2 times 3dim vector)

    Args:
        point_set_a (np.ndarray): nx3 or nx4 mastrix of points
        point_set_b (np.ndarray):  nx3 or nx4 mastrix of points
        hom_matrix (np.ndarray):  4x4 homogenous matrix mapping from a->b

    Returns:
        List[np.ndarray, np.ndarray]: rmse and mae as 1x3 vectors
    """
    num_points = point_set_a.shape[0]
    # First check and possible augment
    if point_set_a.shape[1] == 3:
        ones = np.ones((num_points, 1))
        point_set_a = np.hstack((point_set_a, ones))
        point_set_b = np.hstack((point_set_b, ones))

    # lets do it weirdly just to be sure numpy is doing it correclty
    error = np.empty_like(point_set_a)
    for i in range(num_points):
        error[i, :] = point_set_b[i, :]-hom_matrix@point_set_a[i, :]

    # cut augmented column
    error = error[:, :3]
    abs_error = np.abs(error)
    mean_abs_error = np.mean(abs_error, 0)
    squared_error = error**2
    mean_squared_error = np.mean(squared_error, 0)
    rmse = np.sqrt(mean_squared_error)
    return rmse, mean_abs_error


def get_angle_from_rot_matrix(rot_matrix) -> float:
    # https://en.wikipedia.org/wiki/Rotation_matrix#Determining_the_angle
    temp = (np.trace(rot_matrix)-1)/2
    return 1/np.cos(temp)
