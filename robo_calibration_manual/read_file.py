"""module to read in data from file into matrix, 

"""
from typing import List
import os
from pathlib import Path

from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R

from config.consts import PATH_TO_VIVE_CALIBRATION, DISTANCE_VIVE_ENDEFFECTOR, PATH_TO_ROBOT_CALIBRATION


def readViveData(fileLocation: Path):
    return np.loadtxt(fileLocation, delimiter=" ", skiprows=2)


def get_vive_calibration_positions(date: str, experiment_number: str) -> List[np.ndarray]:
    """Imports measurement data from a vive written to file. This function handles\
            the import of all measurement points taken during (date,experimentnumber)

            The location is a directory whose path is set via env. Therein multiple
            folder with the name structure "{date}_CalibrationSet_{number}" live. Inside each
            are multiple files. Each file identifies a unique measurement set

            The order is important as signified by the numbering of the measurement
            files

            calibration_point_{x}.txt
    Args:
        date (string): [date of experiment, format yyyymmdd
        experimentNumber (str): number identifying the experiment/calibration on that date

    Returns:
        [list of numpy arrays]: list of measurements taken at individual. format is \
                x,y,z,w,i,j,k
    """
    folder_to_load_from = Path(PATH_TO_VIVE_CALIBRATION, date +
                               "_CalibrationSet_" + experiment_number)

    file_naming_scheme: str = "calibration_point_"
    vive_tracker_pose_list = []
    counter = 1
    # file reading hinges on the files being named in ascending manner
    try:
        while True:
            path_to_file = folder_to_load_from.joinpath(
                file_naming_scheme + str(counter)+".txt")
            vive_tracker_pose_list.append(readViveData(path_to_file))
            counter += 1
    except OSError:
        logger.debug(f"es wurden {counter-1}Punkte importiert")
    return vive_tracker_pose_list


def get_calibration_points_quaternion(vive_tracker_pose_list: List[np.ndarray]) -> np.ndarray:
    """calculates the position of the calibration point in LH coordinates

    For every 

    Args:
        vive_tracker_pose_list (List[np.ndarray]): [description]

    Returns:
        np.ndarray: [description]
    """
    res = np.zeros([len(vive_tracker_pose_list), 3])
    calibration_point_in_tracker_kos = np.array(
        [0, 0, DISTANCE_VIVE_ENDEFFECTOR]).reshape([-1, 1])
    for a, calib_pose in enumerate(vive_tracker_pose_list):
        x, y, z, w, i, j, k = np.mean(calib_pose, axis=0)
        rot_matrix_tracker_2_LH = R.from_quat([i, j, k, w])
        pos_tracker_in_LH = np.array([x, y, z]).reshape([-1, 1])
        calib_point_in_LH = rot_matrix_tracker_2_LH\
            .as_matrix()@calibration_point_in_tracker_kos+pos_tracker_in_LH
        res[a, :] = calib_point_in_LH.flatten()
    return res


def get_calibration_points_matrix(vive_tracker_pose_list: List[np.ndarray]) -> np.ndarray:
    """calculates the position of the calibration point in LH coordinates

    For every 

    Args:
        vive_tracker_pose_list (List[np.ndarray]): [description]

    Returns:
        np.ndarray: [description]
    """
    res = np.zeros([len(vive_tracker_pose_list), 3])
    calibration_point_in_tracker_kos = np.array(
        [0, 0, DISTANCE_VIVE_ENDEFFECTOR]).reshape([-1, 1])
    for a, calib_pose in enumerate(vive_tracker_pose_list):
        calib_pose = np.mean(calib_pose, axis=0)
        rot_matrix_tracker_2_LH = calib_pose.reshape([3, 4])
        rot_matrix_tracker_2_LH = np.vstack([rot_matrix_tracker_2_LH, [0, 0, 0, 1]])
        calib_point_in_LH = rot_matrix_tracker_2_LH@np.vstack([calibration_point_in_tracker_kos, 1])
        res[a, :] = calib_point_in_LH.flatten()[:-1]
    return res


def get_calibration_points(vive_tracker_pose_list: List[np.ndarray]) -> np.ndarray:
    """calculates the position of the calibration point in LH coordinates

    For every 

    Args:
        vive_tracker_pose_list (List[np.ndarray]): [description]

    Returns:
        np.ndarray: [description]
    """
    if vive_tracker_pose_list[0].shape[1] == 12:
        return get_calibration_points_matrix(vive_tracker_pose_list)
    elif vive_tracker_pose_list[0].shape[1] == 7:
        return get_calibration_points_quaternion(vive_tracker_pose_list)
    else:
        raise ValueError("The pose have incorrect format. Neither matrix nor quaternion")


def get_robot_data(date: str, experiment_number: str) -> np.ndarray:
    file_dir = Path(PATH_TO_ROBOT_CALIBRATION)
    file_path = file_dir.joinpath(date+"_CalibrationSet_"+experiment_number+".txt")
    return np.loadtxt(file_path, delimiter=" ", skiprows=1)


if __name__ == "__main__":
    experiment_number = "1"
    date = "20210406"
    v = get_vive_calibration_positions(date=date, experiment_number=experiment_number)
    a = get_calibration_points(v)

    # experiment_number = "1"
    # v = get_vive_calibration_positions(date=date, experiment_number=experiment_number)
    # b = get_calibration_points(v)

    # print(b[0])
    print(a[0])
