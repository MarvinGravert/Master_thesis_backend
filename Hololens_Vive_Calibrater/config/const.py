from decouple import config


TCP_HOST = config("TCP_HOST", cast=str, default="0.0.0.0")
TCP_PORT = config("TCP_PORT", cast=int, default=15005)

GRPC_HOST = config("GRPC_HOST", cast=str, default="[::]")
GRPC_PORT = config("GRPC_PORT", cast=int, default=50051)
