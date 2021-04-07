import grpc
import time

from loguru import logger

import holoViveCom_pb2_grpc
from holoViveCom_pb2 import (
    LighthouseState, Tracker, HandheldController
)

from backend_api.vr_objects import (
    ViveController, ViveTracker
)
from config.const import (
    GRPC_HOST_IP, GRPC_HOST_PORT, GRPC_MAX_MESSAGE_LENGTH, POLLING_FREQUENCY
)
from modules.poller.mock_poller import MockPoller
from modules.poller.vr_poller import VRPoller
from config.api_types import (
    VRConfigError, OpenVRConnectionError, StartupError
)


class ForwardLighthouseData():

    def __init__(self) -> None:
        self._grpc_options = [
            ("grpc.max_message_length", GRPC_MAX_MESSAGE_LENGTH),
            ("grpc.max_send_message_length", GRPC_MAX_MESSAGE_LENGTH),
            ("grpc.max_receive_message_length", GRPC_MAX_MESSAGE_LENGTH)
        ]
        # self._poller = MockPoller()
        try:
            self._poller = VRPoller(config_file_path="./vr_object_config.json")
            self._poller.start()
        except (VRConfigError, OpenVRConnectionError):
            raise StartupError

    def connect(self) -> None:

        with grpc.insecure_channel(f"{GRPC_HOST_IP}:{GRPC_HOST_PORT}", self._grpc_options) as channel:
            grpc.channel_ready_future(channel).result(timeout=60)  # Wait max 60 sec for result
            stub = holoViveCom_pb2_grpc.BackendStub(channel=channel)
            logger.info(f"Connecting to {GRPC_HOST_IP}:{GRPC_HOST_PORT}")

            def batch_iterator():
                last_time = time.time()
                while True:
                    state_dict = self._poller.poll()
                    # logger.debug(state_dict)
                    holo_tracker = state_dict.get("holo_tracker", None)
                    calibration_tracker = state_dict.get("calibration_tracker", None)
                    controller = state_dict.get("controller", None)
                    t = LighthouseState(
                        holoTracker=holo_tracker,
                        caliTracker=calibration_tracker,
                        controller=controller)
                    # logger.debug(t)
                    yield t
                    # run loop on frequency
                    current_time = time.time()
                    while current_time-last_time < 1/POLLING_FREQUENCY:
                        current_time = time.time()
                    last_time = current_time
            stub.LighthouseReport(batch_iterator())
