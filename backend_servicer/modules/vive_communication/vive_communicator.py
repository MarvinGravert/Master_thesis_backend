
import asyncio
from typing import Dict

from loguru import logger
import grpc
import grpc.experimental.aio

from holoViveCom_pb2 import (
    LighthouseState, Empty)
import holoViveCom_pb2_grpc

from api.general_types import ServerState
from config.const import (
    WAYPOINT_MANAGER_HOST, WAYPOINT_MANAGER_PORT
)


class ViveCommunicator(holoViveCom_pb2_grpc.BackendServicer):

    def __init__(self, IP: str, port: int, vr_state: ServerState) -> None:
        super().__init__()
        self._IP = IP
        self._port = port
        self.vr_state = vr_state  # TODO: Look into singleton pattern for python

    async def start(self):
        logger.info(f"Async gRPC Server started on {self._IP}:{self._port}")
        grpc.experimental.aio.init_grpc_aio()  # initialize the main loop

        server = grpc.experimental.aio.server()

        server.add_insecure_port(f"{self._IP}:{self._port}")

        holoViveCom_pb2_grpc.add_BackendServicer_to_server(self, server)

        await server.start()
        try:
            await server.wait_for_termination()
        except KeyboardInterrupt:
            # Shuts down the server with 0 seconds of grace period. During the
            # grace period, the server won't accept new connections and allow
            # existing RPCs to continue within the grace period.
            await server.stop(0)

    async def LighthouseReport(self, stream, context) -> Empty:
        """receives updates about all the connected VRObjects and updates
        internal state

        Data is streamed in continously
        """
        logger.info(f"Received a connection from {context.peer()}")
        full_update: Dict[str, bool] = {  # TODO: Find better data strcuture
            "controller": False,
            "holo_tracker": False,
            "calibration_tracker": False
        }
        tracker_update: Dict[str, bool] = {
            "holo_tracker": False,
            "calibration_tracker": False
        }
        async for part in stream:
            logger.debug(f"Received information {part}")
            """
            ----------
            Holo Tracker
            ----------
            """
            if part.HasField("holoTracker"):
                self.vr_state.update_holo_tracker(part.holoTracker)
                full_update["holo_tracker"] = True
                tracker_update["holo_tracker"] = True
            """
            ----------
            Calibration Tracker
            ----------
            """
            if part.HasField("caliTracker"):
                self.vr_state.update_calibration_tracker(part.caliTracker)
                full_update["calibration_tracker"] = True
                tracker_update["calibration_tracker"] = True
            """
            ----------
            Controller
            ----------
            """
            if part.HasField("controller"):
                self.vr_state.update_controller(part.controller)
                full_update["controller"] = True
            """
            ----------
            Trigger new data listeners
            ----------
            """
            # tell subscribers about an update in data
            # problem here=>update is triggered if maybe only 1 device has changed
            # => better may be to have seperate listeners for the devices
            if sum(full_update.values()) == 3:
                for event in self.vr_state.new_full_state_subscriber.values():
                    event.set()
                for key in full_update.keys():
                    full_update[key] = False
            if sum(full_update.values()) == 2:
                for event in self.vr_state.new_tracker_state_subscriber.values():
                    event.set()
                for key in tracker_update.keys():
                    tracker_update[key] = False
            if self.vr_state.controller.menu_button_pressed_down:
                self.vr_state.controller.menu_button_pressed_down = False
                await self.notify_way_point()
                self.vr_state.status = "cmd_place_waypoint"

        return Empty()

    async def ProvideLighthouseState(self, request, context):
        """returns information regarding all tracked objects 

        the client sends the number of unique information he wants to receive


        this methods waits until controller and all trackers have been set
        """
        logger.info(f"Received a connection from {context.peer()}")
        logger.debug("Checking if trackers and controllers have been initialized")
        client_id = str(context.peer())
        self.vr_state.new_full_state_subscriber[client_id] = asyncio.Event()
        # TODO: put into try/except for connection lost so that the deletion of the key
        # is ensured
        """
            ----------
            SETUP Done. Waiting for objects
            ----------
        """
        self.vr_state.new_full_state_subscriber[client_id].set()  # there should be data now
        logger.debug(f"Starting to assemble {request.numberSamples} unique data")
        """
            ----------
            Stream back information
            ----------
        """
        for _ in range(request.numberSamples):
            # wait until a new state arrives
            await self.vr_state.new_full_state_subscriber[client_id].wait()
            self.vr_state.new_full_state_subscriber[client_id].clear()
            logger.debug("yielding new controller/tracker information")
            yield LighthouseState(
                controller=self.vr_state.controller.get_as_grpc_object(),
                holoTracker=self.vr_state.holo_tracker.get_as_grpc_object(),
                caliTracker=self.vr_state.calibration_tracker.get_as_grpc_object())
        """
            ----------
            Stream is finished Clean up
            ----------
        """
        logger.info(f"Connection {client_id} done. Cleaning up")
        del self.vr_state.new_full_state_subscriber[client_id]

    # TODO: refactor implementation to avoid code duplication
    # NOTE: this method is necessary as the controller may not send update (e.g. not in sight)
    # hence we would wait endlessy for a update
    async def ProvideTrackerState(self, request, context):
        """returns information regarding tracker currently registered with the server

        the client sends the number of unique information he wants to receive


        this methods waits until all trackers have been set
        """
        logger.info(f"Received a connection from {context.peer()}")
        logger.debug("Checking if both trackers have been initialized")
        client_id = str(context.peer())
        self.vr_state.new_tracker_state_subscriber[client_id] = asyncio.Event()
        """
            ----------
            SETUP Done. Waiting for objects
            ----------
        """
        self.vr_state.new_tracker_state_subscriber[client_id].set()  # there should be data now
        logger.debug(f"Startin to assemble {request.numberSamples} unique data")
        """
            ----------
            Stream back information
            ----------
        """
        for _ in range(request.numberSamples):
            # wait until a new state arrives
            await self.vr_state.new_tracker_state_subscriber[client_id].wait()
            self.vr_state.new_tracker_state_subscriber[client_id].clear()
            logger.debug("yielding new tracker information")
            yield LighthouseState(
                holoTracker=self.vr_state.holo_tracker.get_as_grpc_object(),
                caliTracker=self.vr_state.calibration_tracker.get_as_grpc_object())
        """
            ----------
            Stream is finished Clean up
            ----------
        """
        logger.info(f"Connection {client_id} done. Cleaning up")
        del self.vr_state.new_tracker_state_subscriber[client_id]

    async def UpdateCalibrationInfo(self, request, context) -> Empty:
        """receives calibration and updates internal calibration
        """
        logger.info(f"Received a connection from {context.peer()}")
        logger.debug("Processing received calibration update")
        self.vr_state.calibration.set_calibration_via_grpc_object(request)
        logger.info("New calibration has been set and will be incorparated into the information flow")
        return Empty()

    async def ChangeStatus(self, request, context) -> Empty:
        """Changes the internal state 

        """
        logger.info(f"Received a connection from {context.peer()}")
        logger.debug("Change the system state")
        self.vr_state.status = request.status
        logger.info(f"New State has been set to: {self.vr_state.status}")
        return Empty()

    async def notify_way_point(self):
        """this method notifies the way point manager that the menu button has been
        pressed and thus a waypoint shall be placed.
        Along with this the controller position is passed
        """
        logger.info("Starting Connection to waypoint manager")
        async with grpc.aio.insecure_channel(f"{WAYPOINT_MANAGER_HOST}:{WAYPOINT_MANAGER_PORT}") as channel:
            logger.info(
                f"Started {self.__class__.__name__} communicator")
            stub = holoViveCom_pb2_grpc.BackendStub(channel=channel)
            """
            Build the message and send
            """
            controller_obj = self.vr_state.controller.get_as_grpc_object()
            logger.debug(f"Sending: {controller_obj}")
            reply = await stub.PlaceWayPoint(LighthouseState(controller=controller_obj))

        logger.info("Way point manager has been notified")
