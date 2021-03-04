from typing import Dict, List

from holoViveCom_pb2 import (
    Tracker, HandheldController, Quaternion
)


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


class ViveController(VRObject):
    def __init__(self,
                 ID: str,
                 location_rotation: List[float],
                 location_tranlation: List[float],
                 button_state: Dict[str, str]) -> None:
        super().__init__(ID, location_rotation, location_tranlation)
        self._button_state = button_state

    def get_as_grpc_object(self) -> HandheldController:
        quat = Quaternion(quat=self.loc_rot)
        trans = self.loc_trans
        return HandheldController(
            ID=self.ID,
            rotation=quat,
            position=trans,
            button_state=self._button_state
        )


class OpenVRConnectionError (Exception):
    # thrown if error while trying to connect and access openvr
    pass


class VRConfigError(Exception):
    # thrown if there is an incorrect path or config settings are wrong
    pass


class StartupError(Exception):
    pass
