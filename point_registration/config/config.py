from decouple import config


"""
Server parameters
"""
POINT_REGISTERING_PORT = config("POINT_REGISTERING_PORT", cast=int, default=50052)
POINT_REGISTERING_HOST = config("POINT_REGISTERING_HOST", cast=str, default="[::]")
MAX_WORKERS = config("MAX_WORKERS", cast=int, default=2)


"""
RANASC Default Parameters
"""
RANSAC_THRESHOLD = config("RANSAC_THRESHOLD", cast=float, default=0.15)
RANSAC_CONFIDENCE = config("RANSAC_CONFIDENCE", cast=float, default=0.8)
