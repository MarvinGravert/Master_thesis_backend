"""Script to evaluate the transformation received via registration.
For every registration received we are logging the points  as well as the calculated matrix. 
For the evualutation we collect more point pairs seperate from this one. So either:
Option A:
1. Take 4 Perspectives=>find transformation
2. Take point pairs at another 2 postion=> apply previously found transformatoin
=> calibrate and test
Standard method
Option B:
1. Take 4 Perspectives=>find transformation
2. move calibratoin object to other position, redo aligning process apply prviously
transformation=>reprojection error depending on distance from initial calibration
Shows the degredation of the quality due to angle error gaining more weight
=> aka how good the angular aligning is
Option C: (implemented on hololens purely)
1. Find transformation 
2. Apply it to real object to get virtual model near it
3. Move virtual object to align with real
4. Distance moved =>registration error 
More context so actual virtual-real relationship (end ot end registration evaluation)


"""
from os import path
from pathlib import Path

import numpy as np
from backend_utils.linear_algebra_helper import calc_reprojection_error, single_reprojection_error, reprojection_error_axis_depending


def load_points_from_file(path_to_file: Path) -> np.ndarray:
    return np.loadtxt(path_to_file.open(mode="r"), skiprows=1)


"""
Matrix to Evalate:
"""
registration_matrix = """
0.89245719 -0.00868954 0.4510484 1.3099407
-0.02266234 0.9994157 -0.0255864 -0.16905557
-0.45056251 -0.03305658   -0.89213264 -1.11754632
0.000000000000000000e+00 0.000000000000000000e+00 0.000000000000000000e+00 1.000000000000000000e+00
"""
registration_matrix = np.fromstring(registration_matrix, dtype=float, sep=" ")
registration_matrix = registration_matrix.reshape((4, 4))

"""
Load points to check matrix against
"""
folder_name = "20210724022235"  # enter folder data


folder_path = Path("./registration_data", folder_name)
real_points_path = folder_path.joinpath("real_points.txt")
virtual_points_path = folder_path.joinpath("virtual_points.txt")

real_points = load_points_from_file(real_points_path)
virtual_points = load_points_from_file(virtual_points_path)

"""
Calculate the reprojection error
Matrix is from real->virtual
"""

# ROOOT OR DEVIATION AS REPROJECTION ERROR if root then add it in point registerin1!!
t, x, s = calc_reprojection_error(real_points, virtual_points, registration_matrix)
print(t)
print(x)
print(s)
