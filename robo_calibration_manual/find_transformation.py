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
from utils.linear_algebra_helper import separate_from_homogeneous_matrix


def run(point_set_1: np.ndarray,
        point_set_2: np.ndarray,
        algorithm: Algorithm = Algorithm(type=Algorithm.Type.ARUN)
        ) -> Tuple[np.ndarray, np.ndarray]:
    """Creates the GRPC Stub to communicate with the point registration service
    forwards the received parameters and returns the rotation R and translation t

        Transformation is from Set 1 to Set 2
    Args:
        point_set_1 (np.ndarray): nx3 set of points in Frame A
        point_set_2 (np.ndarray): nx3 set of points in Frame B
        algorithm (point_set_registration_pb2.Algorithm): GRPC object defining the Algorithm

    Returns:
        R (np.ndarray): 3x3 rotation matrix
        t (np.ndarray): 3x1 translation vector
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


def run_with_config(point_set_1: np.ndarray,
                    point_set_2: np.ndarray,
                    algorithm_config: Dict[str, Any]
                    ) -> Tuple[np.ndarray, np.ndarray]:
    """Creates GRPC request to poitn registration service with handed parameters
    and returns a rotation matrix R and a translation vector t

    It is tried to align Point set 1 with Point set 2. Hence 1->2 is the direction
    of rotational alignment

    The algorithm_config contains information about the algorithm to be performed
    on the point_sets. A blueprint looks as follows:

    algorithm_dict={
        "type": "ARUN"#"OPENCV", "KABSCH", "UMEYAMA"  are also options though the later two
        are repetition
        "optimize": True #boolean, False
        "ranscac": [threshold, confidence] #list of floats
    }

    Args:
        point_set_1 (np.ndarray): point set 1
        point_set_2 (np.ndarray): point set 2
        algorithm_config (Dict[str,str]): configuration describing the algorithm

    Returns:
        Tuple[np.ndarray,np.ndarray]: R, t
    """
    # just build the configuration from the dict and then use the run function
    logger.info("Starting the building the config from the dictionary")
    logger.debug(f"{algorithm_config=}")
    optimize: bool = algorithm_config.get("optimize", False)
    ransac_parameters: List[float, float] = algorithm_config.get("ransac", None)
    type: str = algorithm_config.get("type", "ARUN")

    if ransac_parameters is not None:
        algorithm = Algorithm(type=Algorithm.Type.Value(type),
                              optimize=optimize,
                              ransac=RANSACParameters(
            threshold=ransac_parameters[0],
            confidence=ransac_parameters[1]
        )
        )
        return run(point_set_1=point_set_1, point_set_2=point_set_2, algorithm=algorithm)
    else:
        algorithm = Algorithm(type=Algorithm.Type.Value(type),
                              optimize=optimize,
                              )
        return run(point_set_1=point_set_1, point_set_2=point_set_2, algorithm=algorithm)


def get_vive_data(date, experiment):
    from read_file import get_calibration_points, get_vive_calibration_positions
    data = get_vive_calibration_positions(date=date, experiment_number=experiment)
    return get_calibration_points(data)


if __name__ == "__main__":
    from read_file import get_robot_data
    logger.info("Running client directly")
    experiment = "1"
    date = "20210408"
    algo = Algorithm(
        type=Algorithm.Type.OPENCV,
        optimize=False,
        ransac=RANSACParameters(threshold=1, confidence=0.95)
    )
    point_set_1 = get_vive_data(date=date, experiment=experiment)  # *1000  # mm
    point_set_2 = get_robot_data(date, experiment)
    R, t = run(point_set_1=point_set_1[:21, :], point_set_2=point_set_2[:21, :], algorithm=algo)
    # print(R, t)
    reprojection_error = list()
    for i in range(24):

        v = R@point_set_1[i].reshape([-1, 1])+t
        # print(v)
        # print(point_set_1[0])
        if i == 0:
            print(point_set_1[i])
            print(v)
            print(point_set_2[i])
            print(v-point_set_2[i].reshape([-1, 1]))
            print(np.linalg.norm(v-point_set_2[i].reshape([-1, 1])))
        reprojection_error.append(np.linalg.norm(v-point_set_2[i].reshape([-1, 1])))
    print(np.mean(np.array(reprojection_error)))

    # print(reprojection_error)
    # print(R)
    # print(t)
