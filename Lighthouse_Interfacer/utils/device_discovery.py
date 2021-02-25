from modules.triad_openvr import triad_openvr


def discover_devices():
    v = triad_openvr()
    print(v.print_discovered_objects)
