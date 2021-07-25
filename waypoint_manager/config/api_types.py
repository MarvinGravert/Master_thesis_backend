from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R


class ServerState():
    def __init__(self):

        hom_matrix_lh2robot = """
        1   0  0 0
        0   1  0 0
        0  0  1  0  
        0 0. 0. 1.      
         """
        self.hom_matrix_LH_Robo = np.ndarray = np.fromstring(hom_matrix_lh2robot,
                                                             dtype=float,
                                                             sep=" ").reshape((4, 4))
