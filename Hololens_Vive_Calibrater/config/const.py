from decouple import config
from config.api import CalibrationObject


TCP_HOST = config("TCP_HOST", cast=str, default="0.0.0.0")
TCP_PORT = config("TCP_PORT", cast=int, default=15005)

BACKEND_HOST = config("BACKEND_HOST", cast=str, default="[::1]")
BACKEND_PORT = config("BACKEND_PORT", cast=int, default=50051)

POINT_REGISTER_HOST = config("POINT_REGISTER_HOST", cast=str, default="[::1]")
POINT_REGISTER_PORT = config("POINT_REGISTER_PORT", cast=int, default=50052)

WAYPOINT_MANAGER_HOST = config("WAYPOINT_MANAGER_HOST", cast=str, default="[::1]")
WAYPOINT_MANAGER_PORT = config("WAYPOINT_MANAGER_PORT", cast=int, default=50053)

CALIBRATION_OBJECT = config("CALIBRATION_OBJECT", cast=CalibrationObject, default="firstprototype")

NUM_LIGHTHOUSE_SAMPLES = config("NUM_LIGHTHOUSE_SAMPLES", cast=int, default=1)
