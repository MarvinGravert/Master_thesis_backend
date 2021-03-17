from decouple import config


POLLING_FREQUENCY = config("POLLING_FREQUENCY", cast=float, default=30)

GRPC_HOST_IP = config("GRPC_HOST_IP", cast=str, default="[::1]")
GRPC_HOST_PORT = config("GRPC_HOST_PORT", cast=int, default="50051")
GRPC_MAX_MESSAGE_LENGTH = config("GRPC_MAX_MESSAGE_LENGTH", cast=int, default=3840 * 2160 * 32)
