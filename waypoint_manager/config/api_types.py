from typing import Any, Dict, List, Union
import asyncio
from enum import Enum

from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R

from holoViveCom_pb2 import CalibrationInfo, Tracker, Quaternion, HandheldController
from backend_api.general import Calibration
from backend_api.vr_objects import VRObject


class ServerState():
    def __init__(self):
        self._holo_tracker = None
        self._controller = None
        self.calibration = Calibration()

    @property
    def holo_tracker(self) -> VRObject:
        return self._holo_tracker

    @holo_tracker.setter
    def holo_tracker(self, new_tracker: VRObject):
        self._holo_tracker = new_tracker

    @property
    def controller(self) -> VRObject:
        return self._controller

    @controller.setter
    def calibration_tracker(self, new_controller: VRObject):
        self._controller = new_controller


class IncorrectMessageFormat(Exception):
    pass
