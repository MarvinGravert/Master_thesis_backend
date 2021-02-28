from decouple import config


TCP_HOST = config("TCP_HOST", cast=str, default="0.0.0.0")
TCP_PORT = config("TCP_PORT", cast=int, default=15005)

BACKEND_HOST = config("BACKEND_HOST", cast=str, default="[::]")
BACKEND_PORT = config("BACKEND_PORT", cast=int, default=50051)

POINT_REGISTER_HOST = config("POINT_REGISTER_HOST", cast=str, default="[::]")
POINT_REGISTER_PORT = config("POINT_REGISTER_PORT", cast=int, default="50052")
