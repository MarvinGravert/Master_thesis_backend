"""this module serves to log all the information regarding the calibration so that it can be 
saved in a file to later check the transformation.

This logs:
- the calibration pose received
- both the tracker poses received
(- which calibration object was used) ToBeDone
- the matrix LH->Virtual
- the matrix Virtual->Tracker
(- the reprojectionError) ToBeDone
"""
import datetime
from pathlib import Path
from typing import List

import numpy as np

from config.api_types import ViveTracker


class DataLogger():
    def __init__(self):
        self.file_path=Path(".","calibration_data",datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        self.calibration_position:List[float]=None#list[float]
        self.calibration_rotation:List[float]=None#i j k w
        self.holo_tracker:ViveTracker=None #VRTracker
        self.calibration_tracker:ViveTracker=None
        self.hom_LH_to_virtual:np.ndarray=None
        self.hom_tracker_to_virtual:np.ndarray=None
        

    def write_to_file(self):
        
        with self.file_path.open(mode="w") as file:
            file.write("Position and Rotation received from hololens \n")
            for i in self.calibration_position:
                file.write(f"{i}   ")
            file.write("\n")
            for i in self.calibration_rotation:
                file.write(f"{i}   ")
            file.write("\n")
            file.write(f"Holotracker_Pose \n")
            np.savetxt(file, self.holo_tracker.get_as_hom_matrix() )
            file.write(f"Calibrationtracker Pose \n")
            np.savetxt(file, self.calibration_tracker.get_as_hom_matrix() )
            file.write("Marix LH->Virtual \n ")
            np.savetxt(file,self.hom_LH_to_virtual,)
            file.write("Matrix Virtual->Tracker\n")
            np.savetxt(file,self.hom_tracker_to_virtual)
      