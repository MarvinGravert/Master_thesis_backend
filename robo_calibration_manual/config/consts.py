from decouple import config

BACKEND_HOST = config("BACKEND_HOST", cast=str, default="[::1]")
BACKEND_PORT = config("BACKEND_PORT", cast=int, default=50051)

NUM_LIGHTHOUSE_SAMPLES = config("NUM_LIGHTHOUSE_SAMPLES", cast=int, default=1)
