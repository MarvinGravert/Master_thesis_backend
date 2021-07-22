from dataclasses import dataclass, field
from typing import Any, Dict, List
import asyncio
from enum import Enum

from loguru import logger
import numpy as np
from scipy.spatial import transform
from scipy.spatial.transform import Rotation as R

from backend_api.general import Calibration
# from backend_api.vr_objects import (
#     ViveController, ViveTracker
# )
from backend_api.grpc_objects import Pose


@dataclass
class Task():
    message: str
    callback_event: asyncio.Event
    transformation: Pose = field(init=False)


class CalibrationObject(Enum):
    FIRSTPROTOTYPE = "firstprototype"
    PROTOTYPEV2 = "secondprototype"


class IncorrectMessageFormat(Exception):
    pass
