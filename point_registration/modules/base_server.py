from typing import Tuple
import numpy as np

from loguru import logger

from point_set_registration_pb2 import Output, MatrixRow, Vector, Algorithm
import point_set_registration_pb2_grpc


from modules.algorithms.kabsch import KabschAlgorithm
from modules.algorithms.opencv import OpencvAlgorithm
from modules.optimization.optimize import Optimizer

class PointSetRegistering(point_set_registration_pb2_grpc.PointSetRegisteringServicer):
    def registerPointSet(self, request, context):
        """
        Process Request
        """
        logger.info("Starting Point Set Registration")
        point_set_1, point_set_2 = self._prepare_data(request)
        if request.algorithm.type in [Algorithm.Type.ARUN, Algorithm.Type.KABSCH]:
            logger.info("Running Kabsch/Arun")
            algorithm=KabschAlgorithm()
            R, t = algorithm.register_point_set(point_set_1, point_set_2)
        elif request.algorithm.type in [Algorithm.Type.OPENCV, Algorithm.Type.UMEYAMA]:
            logger.info("Running OpenCV")
            algorithm=OpencvAlgorithm(request.algorithm.ransac)
            R, t = algorithm.register_point_set(point_set_1, point_set_2)
        else:
            logger.error("Wrong Algorithm Type")
            context.abort()
        logger.debug(f"Result: \n {R=}\n{t=}")
        """
        Optimize
        """
        if request.algorithm.optimize==True:
            logger.info("Running Optimizer")
            opt=Optimizer(point_set_1=point_set_1,point_set_2=point_set_2,R=R,t=t)
            R,t=opt.find_optimal_transformation()
            R=opt.correct_rotation_matrix(R)
            logger.debug(f"Optimization Result: \n {R=}\n{t=}")
            logger.info("Done with Optimisation")
        """
        Prepare response
        """
        logger.info("Building response")
        response = Output(
            rotationMatrix=[MatrixRow(row=x) for x in np.ndarray.tolist(R)],
            translationVector=Vector(entries=t)
        )
        return response

    def _prepare_data(self, request) -> Tuple[np.ndarray, np.ndarray]:
        """Writes the data from the request into two arrays

        Args:
            request ([type]): grpc request containing the data

        Returns:
            Tuple[np.ndarray, np.ndarray]: Tuple of point_set_1 and point_set_2
        """
        logger.info("Preparing Data")
        point_set_1 = list()
        point_set_2 = list()
        for x in request.pointSet_1:
            point_set_1.append(np.array(x.entries))
        point_set_2 = [np.array(x.entries) for x in request.pointSet_2]
        return np.array(point_set_1), np.array(point_set_2)
