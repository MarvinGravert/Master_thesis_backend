from loguru import logger
import numpy as np
from scipy.spatial.transform import Rotation as R


class ServerState():
    def __init__(self):

        hom_matrix_lh2robot = """
         0.97352296  0.01101666 -0.22832374 -140.93940735
        -0.22823046 -0.00910516 -0.97356457 -2205.47338867
        -0.01280435  0.99989784 -0.00634975 1181.50012207
        0 0. 0. 1.     
         """
        self.hom_matrix_LH_Robo = np.ndarray = np.fromstring(hom_matrix_lh2robot,
                                                             dtype=float,
                                                             sep=" ").reshape((4, 4))
