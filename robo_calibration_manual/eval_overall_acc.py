from typing import List, Tuple
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as R
from more_itertools import grouper

from backend_utils.linear_algebra_helper import build_coordinate_system_via_3_points


def get_data_base_path() -> Path:
    return Path("./overall_acc_data")


def read_laser_data(path2file: Path) -> np.ndarray:
    return np.genfromtxt(path2file, delimiter=",", skip_header=1)


def get_laser_data(date: str, experiment_number: int) -> np.ndarray:
    """returns the raw laser data taken from X experiment on the specified date

    Args:
        date (str): yyyymmdd format 
        experiment_number (int): number of experiment

    Returns:
        np.ndarray: nx24 See the raw file to see the column specification
    """
    data_dir = get_data_base_path()
    path2laser_file = data_dir/Path(f"{date}_Exp{experiment_number}.txt")
    return read_laser_data(path2laser_file)


def pre_process_laser_data(laser_data: np.ndarray) -> np.ndarray:
    """cut the laser data down and check if anything has moved during the measuring circles


    Args:
        laser_data (np.ndarray): nx24 array

    Returns:
        np.ndarray: nx3 array
    """
    laser_data = laser_data[:, :3]
    """ 
    CHECKING If MOVED
    Workign in 4point cycles means 0->3 4->7 etc shuold be same location
    """
    # TODO: Implement x)
    return laser_data


def process_laser_data(laser_data: np.ndarray) -> List[np.ndarray]:
    """receives laser data and processes it into hom_matrix
    representing the transformation to the laser tracker center

    Args:
        laser_data (np.ndarray): [description]
    """
    hom_matrix_list = list()
    for origin, x_axis, y_axis, _ in grouper(laser_data, 4):
        hom_point2laser = build_coordinate_system_via_3_points(
            origin=origin,
            x_axis_point=x_axis,
            y_axis_point=y_axis
        )
        hom_matrix_list.append(hom_point2laser)
    return hom_matrix_list


def calculate_distance_points(date: str, exp_num: int):
    # tip of tcp in roboter_laser_kos
    tcp_tip = np.array([51, 51, 93-10, 1])
    # target location for waypoint
    target_loc = np.array([132, 132, -10, 1])

    laser_data = get_laser_data(date, experiment_number=exp_num)
    laser_data = pre_process_laser_data(laser_data)
    print(laser_data)
    list_hom_matrix = process_laser_data(laser_data)

    distance_list = list()
    for hom_target2laser, hom_rob2laser in grouper(list_hom_matrix, 2):
        # target shuold be first
        target_in_laser = hom_target2laser@target_loc
        tcp_tip_in_laser = hom_rob2laser@tcp_tip

        dist = np.linalg.norm(target_in_laser-tcp_tip_in_laser)
        distance_list.append(dist)

    print(distance_list)
    print(f"{np.mean(distance_list)} \u00B1 {np.std(distance_list)}")


if __name__ == "__main__":
    date = "20210730"
    exp_num = 1
    calculate_distance_points(date, exp_num)
