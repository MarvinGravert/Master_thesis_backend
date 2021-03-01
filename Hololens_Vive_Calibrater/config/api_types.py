from typing import Any, Dict, List
import asyncio

from loguru import logger
import numpy as np

from holoViveCom_pb2 import HandheldController, LighthouseState, TrackerState, Quaternion, Tracker


class VRObject():
    def __init__(self,
                 ID: str,
                 location_rotation: List[float],
                 location_tranlation: List[float]) -> None:
        self.ID = ID
        self.loc_rot = location_rotation  # w i j k
        self.loc_trans = location_tranlation  # x y z


class ViveTracker(VRObject):

    def get_as_grpc_object(self) -> Tracker:
        quat = Quaternion(quat=self.loc_rot)
        trans = self.loc_trans
        return Tracker(ID=self.ID, rotation=quat, position=trans)

    def get_as_hom_matrix(self) -> np.ndarray:
        from scipy.spatial.transform import Rotation as R
        rot_matrix = R.from_quat(self.loc_rot)
        trans_vec = np.array(self.loc_trans).reshape([3, 1])
        hom_matrix = np.hstack([
            rot_matrix.as_matrix(),
            trans_vec
        ])  # reshape just to be safe
        hom_matrix = np.vstack([hom_matrix, [0, 0, 0, 1]])
        logger.debug(f"Vive Tracker HOm Matrix is:\n {hom_matrix}")
        return hom_matrix


class VRState():
    def __init__(self):
        self._holo_tracker = None
        self._calibration_tracker = None

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
