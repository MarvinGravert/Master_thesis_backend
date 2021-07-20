from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Dict, List

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

    def as_grpc(self) -> holoViveCom_pb2.Controller:
        return holoViveCom_pb2.Controller(
            name=self.name,
            position=self.position,
            rotation=self.rotation,
            buttonState=self.button_state
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
        for obj in grpc_message.trackerList:
            trackables.append(Tracker(
                name=obj.name,
                position=obj.position,
                rotation=obj.rotation,
            ))
        for obj in grpc_message.controllerList:
            trackables.append(Controller(
                name=obj.name,
                position=obj.position,
                rotation=obj.rotation,
                button_state=obj.buttonState
            ))
        return trackables
