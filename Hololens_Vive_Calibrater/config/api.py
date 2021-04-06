from typing import Any, Dict, List
import asyncio
from enum import Enum

from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R

from holoViveCom_pb2 import HandheldController, LighthouseState, Quaternion, Tracker, CalibrationInfo
from backend_api.general import Calibration
from backend_api.vr_objects import (
    ViveController, ViveTracker
)


class CalibrationObject(Enum):
    FIRSTPROTOTYPE = "firstprototype"
    PROTOTYPEV2 = "secondprototype"


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


class IncorrectMessageFormat(Exception):
    pass
