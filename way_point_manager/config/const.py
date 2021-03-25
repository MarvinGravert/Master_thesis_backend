
from decouple import config

TCP_HOST = config("TCP_HOST", cast=str, default="0.0.0.0")
WAYPOINT_MANAGER_PORT = config("WAYPOINT_MANAGER_PORT", cast=int, default=15006)

BACKEND_HOST = config("BACKEND_HOST", cast=str, default="[::1]")
BACKEND_PORT = config("BACKEND_PORT", cast=int, default=50051)
