from typing import Any, Dict, List
import asyncio

from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R

from holoViveCom_pb2 import HandheldController, LighthouseState, TrackerState, Quaternion, Tracker, CalibrationInfo


class VRObject():
    def __init__(self,
                 ID: str,
                 location_rotation: List[float],
                 location_tranlation: List[float]) -> None:
        self.ID = ID
        self.loc_rot = location_rotation  # w i j k
        self.loc_trans = location_tranlation  # x y z
    def get_pose_as_hom_matrix(self) -> np.ndarray:
            """returns the current pose (postion+quat) as a 4x4 homogenous matrix

            Returns:
                np.ndarray: 4x4 homogenous matrix
            """
            w, i, j, k = self.loc_rot
            rot = R.from_quat([i, j, k, w])  # scipy wants scalar last)
            rot_matrix = rot.as_matrix()
            hom_matrix = np.hstack([rot_matrix, np.array(self.loc_trans).reshape([3, 1])])
            return np.vstack([hom_matrix, [0, 0, 0, 1]])

class ViveTracker(VRObject):

    def get_as_grpc_object(self) -> Tracker:
        quat = Quaternion(quat=self.loc_rot)
        trans = self.loc_trans
        return Tracker(ID=self.ID, rotation=quat, position=trans)

    def get_as_hom_matrix(self) -> np.ndarray:
        w, i, j, k = self.loc_rot
        rot = R.from_quat([i, j, k, w])  # scipy wants scalar last
        trans_vec = np.array(self.loc_trans).reshape([3, 1])
        hom_matrix = np.hstack([
            rot.as_matrix(),
            trans_vec
        ])  # reshape just to be safe
        hom_matrix = np.vstack([hom_matrix, [0, 0, 0, 1]])
        logger.debug(f"Vive Tracker HOm Matrix is:\n {hom_matrix}")
        return hom_matrix

# s = ",".join([str(i) for i in self.loc_trans])+":"
#         s += ",".join([str(i) for i in self.loc_rot])+":"
class Calibration():
    """representation of the calibration matrix which maps from virtual to tracker
    it saves this as a homogenous matrix which can be usd in processing

    Furthermore, a boolean is used to check if calibration has been set as this 
    is simply initialised with an empty calibration
    """

    def __init__(self):
        """initialise the matrix with the base homogenous matrix
        """
        temp_matrix = np.hstack([np.identity(n=3), np.zeros([3, 1])])
        temp_matrix = np.vstack([temp_matrix, np.array([0, 0, 0, 1])])
        self._calibration_matrix: np.ndarray = temp_matrix
        self._calibration_received: bool = False

    @property
    def calibration_matrix(self) -> np.ndarray:
        return self._calibration_matrix

    def set_calibration_via_grpc_object(self, calibration_info: CalibrationInfo) -> None:
        """setting the calibration matrix when handed via gprc_object

        the object is a flattend 4x4 matrix

        Args:
            calibration_info (CalibrationInfo): [description]
        """
        flattend_matrix: np.ndarray = calibration_info.calibrationMatrixRowMajor
        self._calibration_matrix = flattend_matrix.reshape([4, 4])
        logger.debug(f"New calibration has been set to: \n {self.calibration_matrix}")
        # This signifies a received calibration
        self._calibration_received = True

    def get_calibration_as_grpc_object(self) -> CalibrationInfo:
        """returns the calibration matrix as a calibrationInfo gRPC object
        the matrix is simply flattend

        Returns:
            CalibrationInfo: grpc object has definedin proto
        """
        return CalibrationInfo(calibrationMatrixRowMajor=self.calibration_matrix.flatten())

    def calibration_received(self) -> bool:
        return self._calibration_received


class VRState():
    def __init__(self):
        self._holo_tracker = None
        self._calibration_tracker = None
        self.calibration = Calibration()

    @ property
    def holo_tracker(self) -> ViveTracker:
        return self._holo_tracker

    @ holo_tracker.setter
    def holo_tracker(self, new_tracker: ViveTracker):
        self._holo_tracker = new_tracker

    @ property
    def calibration_tracker(self) -> ViveTracker:
        return self._calibration_tracker

    @ calibration_tracker.setter
    def calibration_tracker(self, new_tracker: ViveTracker):
        self._calibration_tracker = new_tracker

    def init_holo_tracker(self, new_state: Tracker) -> None:

        logger.debug("Initing holo_tracker")
        self._holo_tracker = ViveTracker(ID=new_state.ID,
                                         location_rotation=new_state.rotation.quat,
                                         location_tranlation=new_state.position)

    def init_calibration_tracker(self, new_state: Tracker) -> None:

        logger.debug("Initing calibration tracker")
        self._calibration_tracker = ViveTracker(ID=new_state.ID,
                                                location_rotation=new_state.rotation.quat,
                                                location_tranlation=new_state.position)


class IncorrectMessageFormat(Exception):
    pass
