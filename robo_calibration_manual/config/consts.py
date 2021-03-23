from decouple import config

NUM_LIGHTHOUSE_SAMPLES = config("NUM_LIGHTHOUSE_SAMPLES", cast=int, default=1)

PATH_TO_VIVE_CALIBRATION = config("PATH_TO_VIVE_CALIBRATION",
                                  cast=str, default="./vive_calibration_data")
PATH_TO_ROBOT_CALIBRATION = config("PATH_TO_ROBOT_CALIBRATION",
                                   cast=str, default="./robot_calibration_data")
"""
Point registering
"""
POINT_REGISTER_HOST = config("POINT_REGISTER_HOST", cast=str, default="[::1]")
POINT_REGISTER_PORT = config("POINT_REGISTER_PORT", cast=int, default=50052)

"""
RANASC Default Parameters
"""
RANSAC_THRESHOLD = config("RANSAC_THRESHOLD", cast=float, default=0.15)
RANSAC_CONFIDENCE = config("RANSAC_CONFIDENCE", cast=float, default=0.99)
"""
Hardware Parameters
"""
DISTANCE_VIVE_ENDEFFECTOR = config("DISTANCE_VIVE_ENDEFFECTOR", cast=float, default=0.07)
