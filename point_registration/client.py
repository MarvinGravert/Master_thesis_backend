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

from config.config import GRPC_PORT, RUNTIME_HOST


def run(point_set_1:np.ndarray,
        point_set_2:np.ndarray,
        algorithm:Algorithm=Algorithm(type=Algorithm.Type.ARUN)
        )->Tuple[np.ndarray,np.ndarray]:
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
    with grpc.insecure_channel(f"{RUNTIME_HOST}:{GRPC_PORT}") as channel:
        stub = point_set_registration_pb2_grpc.PointSetRegisteringStub(channel)
        logger.info(f"Connecting to {RUNTIME_HOST}:{GRPC_PORT}")

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

    R = list()
    t = list()
    for row, entry in zip(response.rotationMatrix,
                            response.translationVector.entries):
        R.append(row.row)
        t.append(entry)
    R = np.array(R)
    t = np.array(t).reshape([3, 1])

    return R, t




def run_with_config(point_set_1:np.ndarray,
        point_set_2:np.ndarray,
        algorithm_config:Dict[str,Any]
        )->Tuple[np.ndarray,np.ndarray]:
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
    optimize:bool=algorithm_config.get("optimize", False)
    ransac_parameters:List[float,float]=algorithm_config.get("ransac", None)
    type:str=algorithm_config.get("type", "ARUN")

    if ransac_parameters is not None:
        algorithm=Algorithm(type=Algorithm.Type.Value(type),
                            optimize=optimize,
                            ransac=RANSACParameters(
                                threshold=ransac_parameters[0],
                                confidence=ransac_parameters[1]
                                )
                            )
        return run(point_set_1=point_set_1,point_set_2=point_set_2,algorithm=algorithm)
    else:
        algorithm=Algorithm(type=Algorithm.Type.Value(type),
                    optimize=optimize,
                    )
        return run(point_set_1=point_set_1,point_set_2=point_set_2,algorithm=algorithm)

    

def get_data_from_file(file_location_1="point_set_1.txt",
                       file_location_2="point_set_2.txt"
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """Reads data from a text file into a numpy array 
    The rows are determined by \n linebreaks and the columns by " " spaces
    Args:
        file_location_1 (str, optional): location of text file 1. Defaults to "point_set_1.txt".
        file_location_2 (str, optional): location of text file 2. Defaults to "point_set_2.txt".

    Returns:
        Tuple[np.ndarray, np.ndarray]: Tuple of the data matrices 
    """
    logger.debug("Reading Data from files")
    logger.debug(f"File 1 is located at {file_location_1}")
    logger.debug(f"File 2 is located at {file_location_2}")
    return np.loadtxt(file_location_1), np.loadtxt(file_location_2)


if __name__ == "__main__":
    logger.info("Running client directly")
    algo=Algorithm(
        type=Algorithm.Type.OPENCV,
        optimize=True,
        ransac=RANSACParameters(threshold=3,confidence=2)
    )
    point_set_1, point_set_2 = get_data_from_file()
    run(point_set_1=point_set_1, point_set_2=point_set_2 ,algorithm=algo)
