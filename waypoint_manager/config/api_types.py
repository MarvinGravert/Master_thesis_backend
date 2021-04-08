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
        self.LH2Virtual = Calibration("""
        -9.654641747474670410e-01 -1.364452205598354340e-02 -2.601783275604248047e-01 -7.605543732643127441e-01
        -2.596095502376556396e-01 -3.375317901372909546e-02 9.651236534118652344e-01 3.441359281539916992e+00
        -2.195049636065959930e-02 9.993370771408081055e-01 2.904523536562919617e-02 2.274712771177291870e-01
        0.000000000000000000e+00 0.000000000000000000e+00 0.000000000000000000e+00 1.000000000000000000e+00
        """)
        self.LH2Robo = Calibration("""-895.20861816   -5.07594824  396.7756958 361.0440979
                                       416.59625244   -3.82041144  879.37213135 2096.13208008
                                        -1.72926676  974.49450684    3.5913527  1200.68994141    
                                    0.          0.          0.          1.       """)

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
