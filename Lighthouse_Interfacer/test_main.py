"""this main is used to test interactoins and is mainly used with the util functions
"""
import openvr
from openvr.error_code import InitError_Init_PathRegistryNotFound

from utils.triad_openvr import triad_openvr


def discover_devices():
    v = triad_openvr()
    print(v.print_discovered_objects())


def print_controller_pose(config_file=None):
    v = triad_openvr(configfile_path=config_file)
    import time
    while True:
        pose = v.devices["controller_1"].get_pose_quaternion()

        print(pose)
        time.sleep(1)


def print_tracker_pose(config_file=None):
    v = triad_openvr(configfile_path=config_file)
    import time
    while True:
        pose = v.devices["tracker_1"].get_pose_quaternion()

        print(pose)
        time.sleep(1)


def print_controller_button_state(config_file=None):
    v = triad_openvr(config_file)
    import time
    while True:
        buttons = v.devices["controller_1"].get_controller_inputs()

        print(buttons)
        time.sleep(1)


def print_controller_full(config_file=None):
    v = triad_openvr(config_file)
    import time
    while True:
        pose = v.devices["controller_1"].get_pose_quaternion()
        buttons = v.devices["controller_1"].get_controller_inputs()
        print(pose)
        print(buttons)
        time.sleep(1)


def print_device_information():
    v = triad_openvr()
    print(v.print_discovered_objects())


if __name__ == "__main__":
    try:

        discover_devices()
        # print_controller_full()
        print_tracker_pose()
    except InitError_Init_PathRegistryNotFound:
        print("works")
