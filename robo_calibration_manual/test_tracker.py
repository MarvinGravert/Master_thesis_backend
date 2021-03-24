import traceback
from triad_openvr import triad_openvr, convert_to_quaternion
import logging
import time
from datetime import datetime
import os
import sys
import numpy as np
import openvr


def _create_hom_from_vive(data: openvr.HmdMatrix34_t) -> np.ndarray:
    matrix = np.array([
        [data[0][0], data[0][1], data[0][2], data[0][3]],
        [data[1][0], data[1][1], data[1][2], data[1][3]],
        [data[2][0], data[2][1], data[2][2], data[2][3]],
    ])

    return np.vstack([matrix, [0, 0, 0, 1]])


if __name__ == "__main__":

    v = triad_openvr()
    t = triad_openvr()
    v.print_discovered_objects()

    freq = 0.5
    numMeasurements = 1000
    counter = 0
    current_directory = os.path.dirname(__file__)
    while True:
        counter += 1
        startTime = time.time()

        # tracker_pose_in_LH = v.devices["tracker_1"].get_pose_matrix()
        # hom_tracker_2_LH = _create_hom_from_vive(tracker_pose_in_LH)
        # print("trackerPose: \n", np.linalg.inv(hom_tracker_2_LH))
        print(v.devices["tracker_1"].get_pose_quaternion())

        print(v.devices["controller_1"].get_pose_quaternion())
        print(t.devices["controller_1"].get_controller_inputs())
        if counter > numMeasurements:
            break

        endTime = time.time()
        timeDif = endTime-startTime
        if timeDif <= 1/freq:
            time.sleep((1/freq-timeDif))
