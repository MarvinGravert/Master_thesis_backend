
import threading
from triad_openvr import triad_openvr
import logging
from statistics import mean
import time
from datetime import datetime
import os
import sys

printAverageValueFlag = False


def checkIfExists(filename):
    current_directory = os.path.dirname(__file__)
    return os.path.isfile(filename)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    v = triad_openvr.triad_openvr()
    v.print_discovered_objects()

    filename = "./robo_data/calibration_point_23.txt"  # CCR 05
    freq = 250
    numMeasurements = 1000
    counter = 0
    current_directory = os.path.dirname(__file__)
    t = checkIfExists(filename)
    if t:
        print("This file already exists")
        sys.exit()
    with open(filename, 'w') as f:
        # quaternion
        s = "# x y z w j i k Freq: "+str(freq)+" current Time: " + \
            datetime.today().strftime('%Y-%m-%d-%H:%M:%S')+"\n"
        # s="# 3x4 first row second row third row Freq: "+str(freq)+" current Time: "+datetime.today().strftime('%Y-%m-%d-%H:%M:%S')+"\n"##matrix
        f.write(s)
        while True:
            counter += 1
            startTime = time.time()

            poseDataQuat = v.devices["tracker_1"].get_pose_quaternion()
            # poseData = v.devices["tracker_1"].get_pose_matrix()
            print("trackerPose: ", poseDataQuat)

            s = str(poseDataQuat).strip("[] ]").replace(",", "").replace("]", "").replace("[", "")
            f.write(s+"\n")
            if counter > numMeasurements:
                break

            endTime = time.time()
            timeDif = endTime-startTime
            print(timeDif)
            if timeDif <= 1/freq:
                time.sleep((1/freq-timeDif))
