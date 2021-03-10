"""this main is used to test interactoins and is mainly used with the util functions
"""
import openvr
from openvr.error_code import InitError_Init_PathRegistryNotFound
from utils.device_discovery import (
    discover_devices, print_controller_full, print_device_information, print_controller_pose
)
if __name__ == "__main__":
    try:

        discover_devices()
        print_controller_full()
    except InitError_Init_PathRegistryNotFound:
        print("works")
