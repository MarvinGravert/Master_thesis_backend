from decouple import config


TCP_HOST = config("TCP_HOST", cast=str, default="0.0.0.0")
TCP_PORT = config("TCP_PORT", cast=int, default=15004)

GRPC_HOST = config("GRPC_HOST", cast=str, default="[::]")
GRPC_PORT = config("GRPC_PORT", cast=int, default=50051)

WAYPOINT_MANAGER_HOST = config("WAYPOINT_MANAGER_HOST", cast=str, default="[::1]")
WAYPOINT_MANAGER_PORT = config("WAYPOINT_MANAGER_PORT", cast=int, default=50053)
