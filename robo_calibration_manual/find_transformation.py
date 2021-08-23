"""This module allows the connection to the GRPC point registration
server via client interface

As of the time of writing the server offers:
- ARUN (default)
- UMEYAMA called OPENCV (includes a RANSAC)
as point registration algorithm.
Moverover, an nonlinear least square optimizer can be called to further optimize
the result (by default it is turned off though)

In a later a RANSAC will be added. As of now the RANSAC parameters can be handed
over but these will only be used in UMEYAMA case

The point sets are handed as nx3 numpy matrices either to run or run_with_config

They differ in the way the service can be configured. While the first accepts
the GRPC Algorithm object defining the algorithm specification directly the second
offers the option of passing a config dictionary which holds all teh parameters and can
be set without having to import the GRPC libraries
"""
from loguru import logger
from typing import Any, Tuple, Dict, List

import grpc
import numpy as np

from point_set_registration_pb2 import Algorithm, Vector, Input, RANSACParameters
import point_set_registration_pb2_grpc

from config.consts import POINT_REGISTER_HOST, POINT_REGISTER_PORT
from backend_utils.linear_algebra_helper import separate_from_homogeneous_matrix

from read_file import get_robot_endeff_lh_kos, get_robot_endeff_rob_kos
from read_file import get_robot_calibration_pose, get_vive_calibration_pose

tracker2Endeffektor = """
0 1 0 0
1 0 0 0
0 0 -1 80
0 0 0 1
"""
# tracker2Endeffektor = """
# 0 0 -1 0
# -1 0 0 0
# 0 1 0 80
# 0 0 0 1
# """
tracker2Endeffektor = np.fromstring(tracker2Endeffektor, dtype=float, sep=" ").reshape((4, 4))


def run(point_set_1: np.ndarray,
        point_set_2: np.ndarray,
        algorithm: Algorithm = Algorithm(type=Algorithm.Type.ARUN)
        ) -> Tuple[np.ndarray, np.ndarray]:
    """Creates the GRPC Stub to communicate with the point registration service
    forwards the received parameters and returns the rotation R and translation t

        Transformation is from Set 1 to Set 2
    Args:
        point_set_1(np.ndarray): nx3 set of points in Frame A
        point_set_2(np.ndarray): nx3 set of points in Frame B
        algorithm(point_set_registration_pb2.Algorithm): GRPC object defining the Algorithm

    Returns:
        R(np.ndarray): 3x3 rotation matrix
        t(np.ndarray): 3x1 translation vector
    """
    with grpc.insecure_channel(f"{POINT_REGISTER_HOST}:{POINT_REGISTER_PORT}") as channel:
        stub = point_set_registration_pb2_grpc.PointSetRegisteringStub(channel)
        logger.info(f"Connecting to {POINT_REGISTER_HOST}:{POINT_REGISTER_PORT}")

        point_set_1 = [Vector(entries=x) for x in point_set_1]
        point_set_2 = [Vector(entries=x) for x in point_set_2]
        obj_to_send = Input(
            algorithm=algorithm,
            pointSet_1=point_set_1,
            pointSet_2=point_set_2,
        )
        logger.debug(f"Starting request with: {algorithm=}")
        response = stub.registerPointSet(obj_to_send)
    logger.info("Received response, closing RPC")
    logger.debug(f"{response=}")

    hom_matrix = np.reshape(response.transformationMatrixRowMajor, (4, 4))
    R, t = separate_from_homogeneous_matrix(hom_matrix)

    return R, t.reshape((-1, 1))


def point_corres_method(date, experiment_number, rob_file_name):
    algo = Algorithm(
        type=Algorithm.Type.KABSCH,
        optimize=False,
        ransac=RANSACParameters(threshold=6, confidence=0.70)
    )
    point_set_1 = get_robot_endeff_lh_kos(date, experiment_number, 80)  # *1000  # *1000  # mm
    point_set_2 = get_robot_endeff_rob_kos(file_name=rob_file_name)
    print(point_set_1)
    num_for_algo = 11
    R, t = run(
        point_set_1=point_set_1[: num_for_algo, :],
        point_set_2=point_set_2[:num_for_algo, :],
        algorithm=algo)
    # print(R, t)
    logger.error(len(point_set_1[: num_for_algo, :]))
    reprojection_error = list()
    projected_vive_points = list()
    for i in range(21):

        v = R@point_set_1[i].reshape([-1, 1])+t
        projected_vive_points.append(v)
        reprojection_error.append(np.linalg.norm(v-point_set_2[i].reshape([-1, 1])))
    print(reprojection_error)
    print(np.mean(reprojection_error))
    test_reprojection_error = list()
    test_direction_bias_test = list()  # prüfmenge
    test_direction_bias_calib = list()  # kalibriermenge
    for i in range(11, 21):
        v = R@point_set_1[i].reshape([-1, 1])+t
        test_reprojection_error.append(np.linalg.norm(v-point_set_2[i].reshape([-1, 1])))
        test_direction_bias_test.append(v-point_set_2[i].reshape([-1, 1]))
    for i in range(11):
        v = R@point_set_1[i].reshape([-1, 1])+t
        test_direction_bias_calib.append(v-point_set_2[i].reshape([-1, 1]))
    print(test_reprojection_error)
    print(np.mean(test_reprojection_error))
    print(f"direction bias:")
    print(np.array(test_direction_bias_calib))
    from backend_utils.linear_algebra_helper import eval_error_list
    print(eval_error_list(np.array(test_direction_bias_test)[:, 2]))

    from scipy import stats
    print(stats.ttest_1samp(np.array(test_direction_bias_test)[:, 2], 0))
    print(np.array(test_direction_bias_test)[:, 1])
    # from plot_rob_cali_points import plot_calibration_points
    # print(R)
    # print(t)
    # plot_calibration_points(point_set_2, np.array(projected_vive_points))

    # from backend_utils.linear_algebra_helper import combine_to_homogeneous_matrix, calc_reprojection_error
    # homy = combine_to_homogeneous_matrix(
    #     rotation_matrix=R,
    #     translation_vector=t
    # )
    # test = calc_reprojection_error(
    #     point_set_a=point_set_1[:],
    #     point_set_b=point_set_2[:],
    #     hom_matrix=homy
    # )
    # print(test)
    # return test


def direct_hom_lh_2_robot(date, experiment_number, rob_file_name):
    """takes the three rotation matrices(tracker -> lh, tracker -> endeff, endeff -> base)
    to calculate the lh -> base

    transforms the tracker -> lh to milimeters and returns such a matrix as well
    So check if using affine!!

    Args:
        date([type]): [description]
        experiment_number([type]): [description]
        rob_file_name([type]): [description]

    Returns:
        [type]: [description]
    """
    lh2robo_list = list()
    tracker2lh_list = get_vive_calibration_pose(date, experiment_number)
    endeff2base_list = get_robot_calibration_pose(rob_file_name)
    # print(tracker2lh_list[1])
    # for i in tracker2lh_list:
    #     i[:3, 3] = i[:3, 3]*1000
    # print(tracker2lh_list[1])
    for tracker2vive, endeff2base in zip(tracker2lh_list, endeff2base_list):
        lh2robot = endeff2base@tracker2Endeffektor@np.linalg.inv(tracker2vive)
        lh2robo_list.append(lh2robot)
    return lh2robo_list


def direct_method(date, experiment_number, rob_file_name):
    lh2robo_list = direct_hom_lh_2_robot(date, experiment_number, rob_file_name)
    num_points = len(lh2robo_list)
    point_set_1 = get_robot_endeff_lh_kos(date, experiment, 68)  # *1000  # *1000  # mm
    point_set_2 = get_robot_endeff_rob_kos(file_name="20210727_CalibrationSet_1")
    matrix_err_list = list()

    for j in range(num_points):
        err_list = list()
        # print(lh2robo_list[j])
        for i in range(num_points):
            # print(point_set_1[i])
            temp = lh2robo_list[j]@np.append(point_set_1[i], 1)
            # print(temp)
            err = point_set_2[i]-temp[:3]
            err = np.linalg.norm(err)
            err_list.append(err)
        matrix_err_list.append(np.mean(err_list))
    print(matrix_err_list)
    print(np.mean(matrix_err_list))


if __name__ == "__main__":
    logger.info("Running client directly")
    experiment = 6
    date = "20210731"
    rob_file_name = "20210728_CalibrationSet_2"
    point_corres_method(date, experiment, rob_file_name)
    # err_list = list()
    # for i in range(1, 8):
    #     err = point_corres_method(date, i, rob_file_name)
    #     err_list.append(err)
    # print(err_list)

    # direct_method(date, experiment, rob_file_name)
    # print(reprojection_error)
    # print(R)
    # print(t)
