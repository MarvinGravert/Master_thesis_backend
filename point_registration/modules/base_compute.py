import loguru
import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple

from loguru import logger


class BaseAlgorithm(ABC):
    def _check_and_adjust_dimension(self, point_set: np.ndarray
                               ) -> np.ndarray:
        """checks the array if it is either nx3 or 3xn, raises Exception if not
        transposes if  necessary into a 3xn array which is returned

        Args:
            point_set (np.ndarray): [description]

        Raises:
            Exception: [description]

        Returns:
            np.ndarray: [description]
        """
        logger.debug("Checking dimension")
        row, column = point_set.shape
        if row == 3 and column >= 3:
            # column matrix
            return point_set
        elif row >= 3 and column == 3:
            # row matrix
            return point_set.T
        else:
            logger.error("Data is not in correct format")
            raise Exception("Data matrix not correct format")
    @abstractmethod
    def register_point_set(self,
                        points_set_1: np.ndarray,
                        points_set_2: np.ndarray
                        ) -> Tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError
