from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import asyncio

from loguru import logger
from scipy.spatial.transform import Rotation as R
import numpy as np

import holoViveCom_pb2


class MessageObject(ABC):
    @abstractmethod
    def as_grpc(self):
        pass

    @abstractmethod
    def as_string(self):
        pass


@dataclass
class Command(MessageObject):
    command: str

    def as_grpc(self) -> holoViveCom_pb2.Command:
        return holoViveCom_pb2.Command(command=self.command)

    def as_string(self):
        return self.command


@dataclass
class Trackable(MessageObject):
    name: str
    position: List[float]
    rotation: List[float]

    def as_grpc(self):
        pass

    def as_string(self):
        pass


@dataclass
class Tracker(Trackable):
    def as_grpc(self) -> holoViveCom_pb2.Tracker:
        return holoViveCom_pb2.Tracker(
            name=self.name,
            position=self.position,
            rotation=self.rotation
        )

    def as_string(self) -> holoViveCom_pb2.Controller:
        # name:x,y,z:qx,qy,qz,w
        s = self.name
        s += ":"+",".join([str(i) for i in self.position])
        s += ":"+",".join([str(i) for i in self.rotation])
        return s


@dataclass
class Controller(Trackable):
    button_state: Dict[str, str]

    def __post_init__(self):
        # TODO: schedule to remove this and move into lighthouse interface or hololens
        if float(self.button_state['trigger']) < 0.5:
            self.button_state['trigger'] = "False"
        else:
            self.button_state['trigger'] = "True"

    def as_grpc(self) -> holoViveCom_pb2.Controller:
        return holoViveCom_pb2.Controller(
            name=self.name,
            position=self.position,
            rotation=self.rotation
        )

    def as_string(self) -> str:
        # name:x,y,z:qx,qy,qz,w:trackpad_x,trackpad_y,trackpad_pressed,trigger,menu_button,grip_button
        s = self.name
        s += ":"+",".join([str(i) for i in self.position])
        s += ":"+",".join([str(i) for i in self.rotation])
        button_order = ["trackpad_x", "trackpad_y", "trackpad_pressed",
                        "trigger", "menu_button", "grip_button"]
        button_str = ""
        for button_name in button_order:
            button_str += self.button_state[button_name]+","
        # delete last ","
        button_str = button_str[:-1]
        return s+":"+button_str


class TrackableFactory():

    def generateTrackables(self, grpc_message) -> List[Trackable]:
        trackables = []
        for obj in grpc_message.controllerList:
            trackables.append(Tracker(
                name=obj.name,
                position=obj.position,
                rotation=obj.rotation,
            ))
        for obj in grpc_message.trackerList:
            trackables.append(Controller(
                name=obj.name,
                position=obj.position,
                rotation=obj.rotation,
                button_state=obj.button_state
            ))
        return trackables


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
        self.message_obj_dict["calibrationTracker"] = Tracker(name="CalibrationTracker",
                                                              position=[0, 0, 0],
                                                              rotation=[0, 0, 0, 1])
        self.message_obj_dict["holoTracker"] = Tracker(name="CalibrationTracker",
                                                       position=[0, 0, 0],
                                                       rotation=[0, 0, 0, 1])
        self.message_obj_dict["mainController"] = Controller(name="CalibrationTracker",
                                                             position=[0, 0, 0],
                                                             rotation=[0, 0, 0, 1],
                                                             zero_button_state={
                                                                 "trackpad_x": "0.0",
                                                                 "trackpad_y": "0.0",
                                                                 "trackpad_pressed": "False",
                                                                 "trigger": "0",
                                                                 "menu_button": "False",
                                                                 "grip_button": "False"
                                                             })
