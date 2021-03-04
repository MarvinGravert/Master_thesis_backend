from utils.triad_openvr import triad_openvr


def discover_devices():
    v = triad_openvr()
    print(v.print_discovered_objects())

def print_controller_pose(config_file=None):
    v=triad_openvr(configfile_path=config_file)
    import time
    while True:
        pose = v.devices["controller_1"].get_pose_quaternion()

        print(pose)
        time.sleep(1)


def print_controller_button_state(config_file=None):
    v=triad_openvr(config_file)
    import time
    while True:
        buttons = v.devices["controller_1"].get_controller_inputs()

        print(buttons)
        time.sleep(1)

def print_controller_full(config_file=None):
    v=triad_openvr(config_file)
    import time
    while True:
        pose = v.devices["controller_1"].get_pose_quaternion()
        buttons = v.devices["controller_1"].get_controller_inputs()
        print(pose)
        print(buttons)
        time.sleep(1)

def print_device_information():
    v=triad_openvr()
    print(v.print_discovered_objects())


