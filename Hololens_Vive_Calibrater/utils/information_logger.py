"""this module serves to log all the information regarding the calibration so that it can be
saved in a file to later check the transformation.

This logs:
- the calibration pose received
- both the tracker poses received
- which calibration object was used
- the matrix LH->Virtual
- the matrix Virtual->Tracker
- the reprojectionError
"""
import datetime
from pathlib import Path
from typing import List

import numpy as np

from backend_api.vr_objects import ViveTracker


class DataLogger():
    def __init__(self):
        """
            ------------------
            General setup
            ------------------
        """
        self.calibration_directory = Path(".", "calibration_information")
        self.file_path = self.calibration_directory.joinpath(
            datetime.datetime.now().strftime("%Y%m%d%H%M%S")+".txt")
        """
            ------------------
            objects to log
            ------------------
        """
        self.hololens_message: List[str] = None
        self.calibration_position: List[float] = None  # list[float]
        self.calibration_rotation: List[float] = None  # i j k w
        self.holo_tracker: ViveTracker = None  # VRTracker
        self.calibration_tracker: ViveTracker = None
        self.hom_LH_to_virtual: np.ndarray = None
        self.hom_tracker_to_virtual: np.ndarray = None
        self.reprojection_error: float = None
        self.calibration_object: str = None
        self.virtual_points: np.ndarray = None
        self.real_points: np.ndarray = None

    def write_to_file(self):
        """writes the logged information to file. Hereby, the path may be created
        """
        self.calibration_directory.mkdir(parents=True, exist_ok=True)
        with self.file_path.open(mode="w") as file:
            """
            ------------------
            Data virtual object
            ------------------
            """
            file.write("Data received from the hololens:\n")
            file.write(f'{"".join(self.hololens_message)}\n')
            file.write("Position and Rotation received from hololens \n")
            file.write("Pay attention: Left handed KOS and quaternion with scalar last\n")
            # for i in self.calibration_position:
            position = " ".join([str(x) for x in self.calibration_position])
            file.write(position)
            file.write("\n")
            rotation = " ".join([str(x) for x in self.calibration_rotation])
            file.write(rotation)
            file.write("\n")
            """
            ------------------
            Holotracker
            ------------------
            """
            file.write(f"Holotracker Pose: Tracker->LH\n")
            file.write("x y z\n")
            position = " ".join([str(x) for x in self.holo_tracker.position])
            file.write(f"{position}\n")
            file.write("w i j k\n")
            rotation = " ".join([str(x) for x in self.holo_tracker.rotation])
            file.write(f"{rotation}\n")
            file.write("Homogenous matrix of Holo Tracker\n")
            np.savetxt(file, self.holo_tracker.get_pose_as_hom_matrix())
            file.write("\n")
            """
            ------------------
            Calibrationtracker
            ------------------
            """
            file.write(f"Calibrationtracker Pose: Tracker->LH\n")
            file.write("x y z\n")
            position = " ".join([str(x) for x in self.calibration_tracker.position])
            file.write(f"{position}\n")
            file.write("w i j k\n")
            rotation = " ".join([str(x) for x in self.calibration_tracker.rotation])
            file.write(f"{rotation}\n")
            file.write("Homogenous matrix of Calibration Tracker\n")
            np.savetxt(file, self.calibration_tracker.get_pose_as_hom_matrix())
            file.write("\n")
            """
            ------------------
            Calibration object used
            ------------------
            """
            file.write(f"CalibrationObject used : \n{self.calibration_object}")
            file.write("\n")
            """
            ------------------
            Point registration service + reprojection error
            ------------------
            """
            file.write("\nMarix LH->Virtual\n")
            np.savetxt(file, self.hom_LH_to_virtual,)
            file.write("\nReprojection error\n")
            file.write(f"{self.reprojection_error}")
            file.write("\n")
            """
            ------------------
            Virtual center to Tracker
            ------------------
            """
            file.write("\nMatrix Virtual->Tracker\n")
            np.savetxt(file, self.hom_tracker_to_virtual)
            file.write("\n")
            """
            ------------------
            Point Data which was used for matching
            ------------------
            """
            file.write("POINTS THAT WERE MATCHED\n\n")
            file.write("Virtual points. Already transformed into Right Hand KOS \n")
            np.savetxt(file, self.virtual_points)
            file.write("\n")
            file.write("Real points\n")
            np.savetxt(file, self.real_points)
