
from decouple import config

TCP_HOST = config("TCP_HOST", cast=str, default="0.0.0.0")
WAYPOINT_MANAGER_TCP_PORT = config("WAYPOINT_MANAGER_PORT", cast=int, default=15006)

GRPC_HOST = config("GRPC_HOST", cast=str, default="[::]")
WAYPOINT_MANAGER_GRPC_PORT = config("WAYPOINT_MANAGER_GRPC_PORT", cast=int, default=50053)

BACKEND_HOST = config("BACKEND_HOST", cast=str, default="[::1]")
BACKEND_PORT = config("BACKEND_PORT", cast=int, default=50051)

NUM_LIGHTHOUSE_SAMPLES = config("NUM_LIGHTHOUSE_SAMPLES", cast=int, default=1)
