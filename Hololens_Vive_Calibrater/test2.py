import numpy as np

from modules.informationLogger.informationLogger import DataLogger
from config.api_types import ViveTracker

if __name__ == "__main__":
    test=DataLogger()
    test.calibration_position=[1,2,3]
    test.calibration_rotation=[0,1,2,0]
    test.holo_tracker=ViveTracker(ID="d",location_rotation=[0,0,1,0],location_tranlation=[1,1,1])
    test.calibration_tracker=ViveTracker(ID="ab",location_rotation=[1,0,0,0], location_tranlation=[10,20,3])
    test.hom_LH_to_virtual=np.array([[1,1],[2,2]])
    test.hom_virtual_to_tracker=np.array([[10,20],[3,2]])
    test.write_to_file()