"""
Find Transformation from Point Set 1 to Point Set 1 using Kabsch algorithm
"""
from typing import Tuple

import numpy as np
import cv2
from loguru import logger

from point_set_registration_pb2 import RANSACParameters

from config.config import RANSAC_CONFIDENCE, RANSAC_THRESHOLD
from modules.base_compute import BaseAlgorithm
class OpencvAlgorithm(BaseAlgorithm):

    def __init__(self,ransac_parameters:RANSACParameters):
        if ransac_parameters is not None:
            self._threshold=ransac_parameters.threshold
            self._confidence=ransac_parameters.confidence
        else:
            self._threshold=RANSAC_THRESHOLD
            self._confidence=RANSAC_CONFIDENCE
    def register_point_set(self, point_set_1: np.ndarray,
                        point_set_2: np.ndarray
                        ) -> Tuple[np.ndarray, np.ndarray]:
        """Find optimal affine transformation between the points sets 


                function used: 
                https://docs.opencv.org/4.0.0/d9/d0c/group__calib3d.html#ga396afb6411b30770e56ab69548724715
        Args:
            point_set_1 (np.ndarray): 3xn 
            point_set_2 (np.ndarray): 3xn

        Returns:
            np.ndarray: returns R (3x3 rot matrix), t (3x1 matrix)
        """
        # Input: expects 3xN matrix of points
        # Returns R,t
        # R = 3x3 rotation matrix
        # t = 3x1 column vector

        A = self._check_and_adjust_dimension(point_set_1)
        B = self._check_and_adjust_dimension(point_set_2)
        A = A.T
        logger.debug(f"\n {A}")
        B = B.T
        logger.debug(f"\n {B}")
        retval, out, inlier = cv2.estimateAffine3D(src=A,
                                                   dst=B,
                                                   ransacThreshold=self._threshold,
                                                   confidence=self._confidence,
                                                   )
        logger.debug(f"Number of point correspondances: {A.shape[0]}")
        logger.debug(
            f"Number of inlier: {sum([1 if x == 1 else 0 for x in inlier])}")

        logger.debug(f"""
            Parameters used for ransac:
            Threshold {self._threshold}
            CONFIDENCE {self._confidence}
        """)
        logger.info(f"Result: \n {out}")

        return out[:, :3], out[:, 3]
