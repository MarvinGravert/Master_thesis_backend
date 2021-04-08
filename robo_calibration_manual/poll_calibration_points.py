import time
import os
import sys

from loguru import logger
from triad_openvr import triad_openvr
from datetime import datetime


printAverageValueFlag = False


def checkIfExists(filename):
    current_directory = os.path.dirname(__file__)
    return os.path.isfile(filename)


def get_new_filename(folder_dir: str) -> str:
    """checks the folder for files that are named calibration_point_*
    and takes the next one available
    """
    file_list = os.listdir(folder_dir)
    # print(file_list)
    if file_list == []:
        return "calibration_point_1.txt"
    max_number = 1
    for file in file_list:
        num = file.split("_")[2].split(".")[0]
        print(num)
        if int(num) > max_number:
            max_number = int(num)
    return f"calibration_point_{max_number+1}.txt"


def take_measurements(filename: str, freq: float = 100, num_measurements: int = 1000,):
    v = triad_openvr()
    v.print_discovered_objects()
    counter = 0
    with open(filename, 'w') as f:
        # quaternion
        # s = "# x y z w j i k Freq: "+str(freq)+" current Time: " + \
        #     datetime.today().strftime('%Y-%m-%d-%H:%M:%S')+"\n"
        s = "# 3x4 first row second row third row Freq: "+str(
            freq)+" current Time: "+datetime.today().strftime('%Y-%m-%d-%H:%M:%S')+"\n"  # matrix
        f.write(s)
        while True:
            counter += 1
            startTime = time.time()

            poseDataQuat = v.devices["tracker_1"].get_pose_quaternion()
            poseData = v.devices["tracker_1"].get_pose_matrix()
            print("trackerPose: ", poseDataQuat)

            s = str(poseData).strip("[] ]").replace(",", "").replace("]", "").replace("[", "")
            f.write(s+"\n")
            if counter > num_measurements:
                break

            endTime = time.time()
            timeDif = endTime-startTime

            if timeDif <= 1/freq:
                time.sleep((1/freq-timeDif))


if __name__ == "__main__":

    # v = triad_openvr()
    # v.print_discovered_objects()

    file_dir = "./vive_calibration_data/20210408_CalibrationSet_1"  # CCR 05
    file_name = file_dir+"/"+get_new_filename(file_dir)
    take_measurements(filename=file_name)
