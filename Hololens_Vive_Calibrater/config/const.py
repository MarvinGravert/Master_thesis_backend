from decouple import config
from config.api import CalibrationObject

TCP_HOST = config("TCP_HOST", cast=str, default="0.0.0.0")
TCP_PORT = config("TCP_PORT", cast=int, default=15005)

POINT_REGISTER_HOST = config("POINT_REGISTER_HOST", cast=str, default="[::1]")
POINT_REGISTER_PORT = config("POINT_REGISTER_PORT", cast=int, default=50052)

CALIBRATION_OBJECT = config("CALIBRATION_OBJECT", cast=CalibrationObject, default="secondprototype")
