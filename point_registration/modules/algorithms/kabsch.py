"""
Find Transformation from Point Set 1 to Point Set 1 using Kabsch algorithm
"""
from typing import Tuple

import numpy as np

from loguru import logger


from modules.base_compute import BaseAlgorithm


class KabschAlgorithm(BaseAlgorithm):

    def register_point_set(self, point_set_1: np.ndarray,
                        point_set_2: np.ndarray
                        ) -> Tuple[np.ndarray, np.ndarray]:
        """Find transformation from set 1 to set 2 using Kabsch
        
            inspired by:
                https://github.com/nghiaho12/rigid_transform_3D
                which is basically implementing the algorithm proposed by Arun
        Args:
            point_set_1 (np.ndarray): 3xn 
            point_set_2 (np.ndarray): 3xn

        Raises:
            Exception: Raises exception if if input matrix is not 3xn or nx3
            ValueError: if sanity ccheck checking dimension of matrix fails

        Returns:
            np.ndarray: returns R (3x3 rot matrix), t (3x1 matrix)
        """
        # Input: expects 3xN matrix of points
        # Returns R,t
        # R = 3x3 rotation matrix
        # t = 3x1 column vector

        A = self._check_and_adjust_dimension(point_set_1)
        B = self._check_and_adjust_dimension(point_set_2)

        # find mean column wise
        centroid_A = np.mean(A, axis=1)
        centroid_B = np.mean(B, axis=1)

        # ensure centroids are 3x1
        centroid_A = centroid_A.reshape(-1, 1)
        centroid_B = centroid_B.reshape(-1, 1)

        # subtract mean
        Am = A - centroid_A
        Bm = B - centroid_B

        H = Am @ np.transpose(Bm)

        # sanity check
        if np.linalg.matrix_rank(H) < 3:
            raise ValueError(
                "rank of H = {}, expecting 3".format(np.linalg.matrix_rank(H)))

        # find rotation
        U, S, Vt = np.linalg.svd(H)
        R = Vt.T @ U.T

        # special reflection case
        if np.linalg.det(R) < 0:
            logger.info(
                "det(R) < R, reflection detected!, correcting for it ...")
            Vt[2, :] *= -1
            R = Vt.T @ U.T

        t = -R @ centroid_A + centroid_B
        return R, t
