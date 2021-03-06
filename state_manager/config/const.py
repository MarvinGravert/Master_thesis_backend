from decouple import config


BACKEND_SERVICER_IP = config("BACKEND_SERVICER_IP", cast=str, default="[::1]")
BACKEND_SERVICER_PORT = config("BACKEND_SERVICER_PORT", cast=int, default=50051)
