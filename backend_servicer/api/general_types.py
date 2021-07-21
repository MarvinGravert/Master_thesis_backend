
from typing import Any, Dict, List
import asyncio

from backend_api.grpc_objects import (
    MessageObject, Controller, Tracker, Command
)

from loguru import logger
from scipy.spatial.transform import Rotation as R
import numpy as np


class ServerState():
    """object who keeps track of the system state
     contains and manages current message objects
    """

    def __init__(self):
        self.new_full_state_subscriber: Dict[str, asyncio.Event] = dict()
        self.new_tracker_state_subscriber: Dict[str, asyncio.Event] = dict()
        self.message_obj_dict: Dict[str:MessageObject] = {}
        self.startup_routine()

    def startup_routine(self):
        """add calibrationTracker, mainController and holoTracker as zerod trackables
        to facilitate functionality 
        """
        self.message_obj_dict["calibrationTracker"] = Tracker(name="calibrationTracker",
                                                              position=[0, 0, 0],
                                                              rotation=[0, 0, 0, 1])
        self.message_obj_dict["holoTracker"] = Tracker(name="holoTracker",
                                                       position=[0, 0, 0],
                                                       rotation=[0, 0, 0, 1])
        self.message_obj_dict["mainController"] = Controller(name="mainController",
                                                             position=[0, 0, 0],
                                                             rotation=[0, 0, 0, 1],
                                                             button_state={
                                                                 "trackpad_x": "0.0",
                                                                 "trackpad_y": "0.0",
                                                                 "trackpad_pressed": "False",
                                                                 "trigger": "False",
                                                                 "menu_button": "False",
                                                                 "grip_button": "False"
                                                             })
        self.message_obj_dict["command"] = Command(command="")
