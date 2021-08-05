from pathlib import Path
from more_itertools.more import only

import numpy as np
from scipy.spatial.transform import Rotation as R
from backend_utils.linear_algebra_helper import (
    transform_to_homogenous_matrix,
    get_angle_from_rot_matrix,
    separate_from_homogeneous_matrix,
    distance_between_hom_matrices
)
from more_itertools import grouper


def get_base_path() -> Path:
    return Path("./end2endregistration_data")


def get_file_path(exp_num):

    return get_base_path()/Path(f"messreihe{exp_num}.txt")


def import_measurement_data(exp_num):
    file: Path = get_file_path(exp_num=exp_num)
    return np.genfromtxt(file, delimiter=" ", skip_header=1)


def eval():
    # listy = [1,2, 3, 4, 5, "5_half", 6] # 1 is the small clib obj
    listy = [2, 3, 4, 5, 6, "5_half"]
    data_list = list()
    for ele in listy:
        data_list.append(import_measurement_data(ele))

    dist_err_list = list()
    angle_err_list = list()
    for data in data_list:
        for virtual, actual in grouper(data, 2):
            virt2holoCenter = transform_to_homogenous_matrix(
                position=virtual[:3],
                quaternion=virtual[3:]
            )
            actual2holoCenter = transform_to_homogenous_matrix(
                position=actual[:3],
                quaternion=actual[3:]
            )
            dist, angle = distance_between_hom_matrices(virt2holoCenter, actual2holoCenter)
            # print(f"{dist=}")
            # print("Winkel:"+str(np.rad2deg(angle)))

            dist_err_list.append(dist)
            angle_err_list.append(angle)
    # print(np.mean(dist_err_list))
    # print(dist_err_list)
    # print(np.rad2deg(np.mean(angle_err_list)))
    # print(np.rad2deg(angle_err_list))
    half_5 = np.array(np.rad2deg(angle_err_list))[-2:]
    # half_5 = np.array(dist_err_list)[-2:]
    from backend_utils.linear_algebra_helper import eval_error_list
    test = np.array(np.rad2deg(angle_err_list))[:-2]
    # test = np.array(dist_err_list)[:-2]

    zero_list = list()
    one_list = list()
    two_list = list()
    three_list = list()
    four_list = list()
    for zero, one, two, three, four in grouper(test, 5):
        zero_list.append(zero)
        one_list.append(one)
        two_list.append(two)
        three_list.append(three)
        four_list.append(four)
    zero_list.append(half_5[0])
    one_list.append(half_5[1])

    print(np.around(np.array(eval_error_list(zero_list)), 3))
    print(np.around(max(zero_list), 3))


if __name__ == "__main__":
    eval()
