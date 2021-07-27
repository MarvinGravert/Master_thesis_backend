"""module to read in data from file into matrix, 

"""
from typing import List
import os
from pathlib import Path
from utils.linear_algebra_helper import combine_to_homogeneous_matrix

from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R

from backend_utils.linear_algebra_helper import transform_to_homogenous_matrix

from config.consts import PATH_TO_VIVE_CALIBRATION, DISTANCE_VIVE_ENDEFFECTOR, PATH_TO_ROBOT_CALIBRATION


def readViveData(fileLocation: Path):
    return np.loadtxt(fileLocation, delimiter=" ", skiprows=2)


def _get_vive_calibration_raw(date: str, experiment_number: int) -> List[np.ndarray]:
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
        experimentNumber (int): number identifying the experiment/calibration on that date

    Returns:
        [list of numpy arrays]: list of measurements taken at individual. format is \
                x,y,z,w,i,j,k
    """
    folder_to_load_from = Path(PATH_TO_VIVE_CALIBRATION, date +
                               "_CalibrationSet_" + str(experiment_number))

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


def get_vive_calibration_pose(date: str, experiment_number: int):
    """Create a list of hom_matrix representing the transfomration between
    tracker and LH. 
    transforms TO MILIMETER
    Args:
        date (str): [description]
        experiment_number (int): [description]
    """
    vive_list = _get_vive_calibration_raw(date, experiment_number)
    hom_matrix_list = list()
    for data in vive_list:
        avg_data = np.mean(data, 0)
        if len(avg_data) == 12:
            matrix = avg_data.reshape((3, 4))
            hom_matrix = np.vstack((matrix, np.array([[0, 0, 0, 1]])))
            hom_matrix[:3, 3] = hom_matrix[:3, 3]*1000

        else:
            pos = avg_data[0:3]*1000
            quat = avg_data[3:]
            hom_matrix = transform_to_homogenous_matrix(position=pos,
                                                        quaternion=quat,
                                                        scalar_first=True)
        hom_matrix_list.append(hom_matrix)

    return hom_matrix_list


def get_robot_calibration_raw(file_name: str) -> np.ndarray:
    file_dir = Path(PATH_TO_ROBOT_CALIBRATION)
    file_path = file_dir.joinpath(f"{file_name}"+".txt")
    return np.loadtxt(file_path, delimiter=" ", skiprows=1)


def get_robot_calibration_pose(file_name: str) -> List[np.ndarray]:
    """takes position and euler angles to caluclate the hom matrix from 
    End effector to robot base system

    kuka robot is used=>intrinsic z y x 

    Args:
        pos_euler_data (np.ndarray): nx6. 0-2 cols: pos 3-5: euler angles zyx

    Returns:
        List[np.ndarray]: list of hom_matrix from end effector to base
    """
    pos_euler_data = get_robot_calibration_raw(file_name=file_name)
    hom_matrix_list = list()
    for data in pos_euler_data:
        pos = data[0:3]
        euler_ang = data[3:]
        rot = R.from_euler("zyx", euler_ang, degrees=True)  # verified correctness if zyx is true
        matrix = rot.as_matrix()
        # not sure if euler angles are base->eff or eff->base soo inv and try
        matrix = np.linalg.inv(matrix)

        hom_matrix = combine_to_homogeneous_matrix(
            rotation_matrix=matrix,
            translation_vector=pos
        )
        hom_matrix_list.append(hom_matrix)

    return hom_matrix_list


def get_robot_endeff_rob_kos(file_name: str) -> np.ndarray:
    """returns the robot endeffektor in rob basis kos

    Args:
        filename (str): [description]

    Returns:
        np.ndarray: nx3 matrix of position 
    """
    data = get_robot_calibration_raw(file_name=file_name)
    return data[:, 0:3]


def get_robot_endeff_lh_kos(date: str, experiment_number: int, offset_z: float) -> np.ndarray:
    """returns the robot endeffektor in lh kos

    Args:
        date (str): [description]
        experiment (int): s
        offset_z (float): offset IN MILIMETERS!!!

    Returns:
        np.ndarray: nx3 matrix of position
    """
    offset_vector = np.array([0, 0, offset_z, 1]).reshape((4, 1))
    list_hom_tracker2lh = get_vive_calibration_pose(date=date, experiment_number=experiment_number)
    num_points = len(list_hom_tracker2lh)
    points = np.ones((num_points, 3))
    for i in range(num_points):
        points[i, :] = (list_hom_tracker2lh[i]@offset_vector).flatten()[:3]
    return points


if __name__ == "__main__":
    experiment_number = 1
    date = "20210727"
    v = get_vive_calibration_pose(date=date, experiment_number=experiment_number)
    t = get_robot_calibration_raw(file_name="20210727_CalibrationSet_1")
    # experiment_number = "1"
    # v = get_vive_calibration_positions(date=date, experiment_number=experiment_number)
    # b = get_calibration_points(v)
    v = get_robot_calibration_pose(t)
    v = get_robot_endeff_lh_kos(date, experiment_number, 0.068)
    # print(b[0])
    print(v)
