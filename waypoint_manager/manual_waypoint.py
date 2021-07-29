from backend_api.general import InterpolationType, Waypoint
from backend_utils.averageQuaternion import averageQuaternions
from backend_api.general import InterpolationType
from backend_utils.linear_algebra_helper import separate_from_homogeneous_matrix
import numpy as np
from scipy.spatial.transform import Rotation as R

hom_matrix_lh2robot = """
     0.972574   -0.03843073 -0.2293967   -152.83439636
    -0.22798836  0.03777178 -0.97293091 -2191.41381836
    0.04605517  0.99854714  0.0279741 1218.31115723
    0 0. 0. 1.     
         """
hom_matrix_LH_Robo = np.ndarray = np.fromstring(hom_matrix_lh2robot,
                                                dtype=float,
                                                sep=" ").reshape((4, 4))


waypoint_matrix = """
0.02223018 -0.54770316 -2.36654513  0.6956492   0.70549193  0.09366519 -0.0978675
"""
waypoint_matrix = np.ndarray = np.fromstring(waypoint_matrix,
                                             dtype=float,
                                             sep=" ").reshape((-1, 7))

pos = waypoint_matrix[:, :3]
quat = waypoint_matrix[:, 3:]

avg_quat = averageQuaternions(quat)
w, i, j, k = avg_quat
print(avg_quat)
target = Waypoint(position=np.mean(pos, 0),
                  rotation=np.array([i, j, k, w]),
                  type=InterpolationType.Linear)
# print(target)

target.apply_offset(np.array([0, -0.0145, 0.1735]))  # offset in m!
# print(target)
target.position = target.position*1000  # change to mm

# print(target)


def get_pos_rot_in_kuka_kos(waypoint: Waypoint, lh2robot):

    cont2lh = waypoint.as_hom_matrix()
    cont2robot = lh2robot@cont2lh
    rot, t = separate_from_homogeneous_matrix(cont2robot)
    # rot is the controller->base but we need base->controller as controller should be
    # waypoint
    rot_base_waypoint = np.linalg.inv(rot)
    euler = R.from_matrix(rot_base_waypoint)
    angles = euler.as_euler('zyx', degrees=True)
    return t, angles


t, angles = get_pos_rot_in_kuka_kos(target, hom_matrix_LH_Robo)

print(f"{t=}   {angles=}")
