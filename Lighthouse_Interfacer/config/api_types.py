from typing import Dict, List

from holoViveCom_pb2 import (
    Tracker, HandheldController, Quaternion
)


class OpenVRConnectionError (Exception):
    # thrown if error while trying to connect and access openvr
    pass


class VRConfigError(Exception):
    # thrown if there is an incorrect path or config settings are wrong
    pass


class StartupError(Exception):
    pass
