from typing import Any, Dict, List
import asyncio

from loguru import logger
from scipy.spatial.transform import Rotation as R
import numpy as np

from holoViveCom_pb2 import (
    HandheldController, Tracker, CalibrationInfo
)

from backend_api.vr_objects import (
    ViveController, ViveTracker
)


class Calibration():
    """class to hold the calibration matrices (e.g. LH to robot and LH to virtual center)
    """

    def __init__(self, calibration_matrix: str =
                 """
                1 0 0 0
                0 1 0 0
                0 0 1 0
                0 0 0 1
                """):
        """init the matrices from strings to make it easier to copy paste new calibration info
        This was done to easier copy and paste calibration matrices from text during debugging
        """
        LH_2_virtual = calibration_matrix

        self._matrix: np.ndarray = np.fromstring(LH_2_virtual,
                                                 dtype=float,
                                                 sep=" ").reshape((4, 4))

    @ property
    def matrix(self) -> np.ndarray:
        return self._matrix

    def set_calibration_via_grpc_object(self, calibration_info: CalibrationInfo) -> None:
        """setting the calibration matrix when handed via gprc_object

        the object is a flattend 4x4 matrix

        Args:
            calibration_info (CalibrationInfo): [description]
        """
        flattend_matrix: List[float] = calibration_info.calibrationMatrixRowMajor
        self._matrix = np.array(flattend_matrix).reshape([4, 4])
        logger.debug(f"New calibration has been set to: \n {self._matrix}")

    def get_calibration_as_grpc_object(self) -> CalibrationInfo:
        """returns the calibration matrix as a calibrationInfo gRPC object
        the matrix is simply flattend

        Returns:
            CalibrationInfo: grpc object has definedin proto
        """
        return CalibrationInfo(calibrationMatrixRowMajor=self._matrix.flatten())
