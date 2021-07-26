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


def get_vive_calibration_raw(date: str, experiment_number: str) -> List[np.ndarray]:
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


def get_vive_calibration_poitns(date: str, experiment_number: int):
    """Create a list of hom_matrix representing the transfomration between
    tracker and LH. 

    Args:
        date (str): [description]
        experiment_number (int): [description]
    """
    vive_list = get_vive_calibration_raw(date, experiment_number)


def get_robot_calibration_points(file_name: str) -> np.ndarray:
    file_dir = Path(PATH_TO_ROBOT_CALIBRATION)
    file_path = file_dir.joinpath(f"{file_name}"+".txt")
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
