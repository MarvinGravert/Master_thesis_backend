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
    def update_state(self, new_data: Tracker):
        # first check if id is the same=>correct tracker if not dont update
        if self.ID is None:
            self.ID = new_data.ID
        if self.ID != new_data.ID:
            logger.warning("WRONG Tracker. ID mismatch")
            return
        self.loc_rot = new_data.rotation.quat
        self.loc_trans = new_data.position

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
        self._button_state = self._adjust_button_states(button_state)

    def update_state(self, new_data: HandheldController):
        # first check if id is the same=>correct controller has been passed
        logger.debug("updating controller state")
        if self.ID != new_data.ID:
            logger.warning("WRONG Controller. ID mismatch")
            return
        self.loc_rot = list(new_data.rotation.quat)
        self.loc_trans = list(new_data.position)
        # logger.debug()
        temp_button = self._adjust_button_states(new_data.button_state)
        self._button_state = temp_button

    def get_state_as_string(self) -> str:
        # x,y,z:w,i,j,k:x_trackpad:trigger,trackpad_pressed, menuButton,grip_button
        # str(bool(triggerButton))+","+str(trackpadPressed)+","+str(menuButton)+","+str(bool(gripButton))
        xState = self._button_state["trackpad_x"]
        yState = self._button_state["trackpad_y"]
        trackpadPressed = self._button_state["trackpad_pressed"]
        triggerButton = self._button_state["trigger"]
        menuButton = self._button_state["menu_button"]
        gripButton = self._button_state["grip_button"]

        s = ",".join([str(i) for i in self.loc_trans+self.loc_rot])+":"
        # add the rest of the buttons to it
        s += xState+":"+triggerButton+","+trackpadPressed+","+menuButton+","+gripButton
        return s

    def _adjust_button_states(self, button_state: Dict[str, str]) -> Dict[str, str]:
        """Adjusts the button states to the liking of the user
        """
        if float(button_state['trigger']) < 0.5:
            button_state['trigger'] = "False"
        else:
            button_state['trigger'] = "True"

        return button_state


class VRState():
    def __init__(self):
        self._holo_tracker = None
        self._calibration_tracker = None
        self._controller = None
        self._controller_set_event = asyncio.Event()
        self._holo_tracker_set_event = asyncio.Event()
        self._calibration_tracker_set_event = asyncio.Event()

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

    @ property
    def controller(self) -> ViveController:
        return self._controller

    @ controller.setter
    def controller(self, new_controller: ViveController):
        self._controller = new_controller

    def update_holo_tracker(self, new_state: Tracker) -> None:
        logger.debug("Updating HoloTracker")
        self._holo_tracker.update_state(new_state)

    def update_calibration_tracker(self, new_state: Tracker) -> None:
        logger.debug("Updating CaliTracker")
        self._calibration_tracker.update_state(new_state)

    def update_controller(self, new_state: HandheldController) -> None:
        logger.debug("Updating Controller")
        self._controller.update_state(new_state)

    def init_holo_tracker(self, new_state: Tracker) -> None:

        logger.debug("Initing holo_tracker")
        self._holo_tracker = ViveTracker(ID=new_state.ID,
                                         location_rotation=new_state.rotation.quat,
                                         location_tranlation=new_state.position)
        self._holo_tracker_set_event.set()

    def init_calibration_tracker(self, new_state: Tracker) -> None:

        logger.debug("Initing calibration tracker")
        self._calibration_tracker = ViveTracker(ID=new_state.ID,
                                                location_rotation=new_state.rotation.quat,
                                                location_tranlation=new_state.position)
        self._calibration_tracker_set_event.set()

    def init_controller(self, new_state: HandheldController):
        logger.debug("Initing controller")
        self._controller = ViveController(ID=new_state.ID,
                                          location_rotation=new_state.rotation.quat,
                                          location_tranlation=new_state.position,
                                          button_state=new_state.button_state)
        logger.debug("Created object")
        self._controller_set_event.set()