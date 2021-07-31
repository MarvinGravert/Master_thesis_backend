from backend_api.general import InterpolationType, Waypoint
from backend_utils.averageQuaternion import averageQuaternions
from backend_api.general import InterpolationType
from backend_utils.linear_algebra_helper import separate_from_homogeneous_matrix
import numpy as np
from scipy.spatial.transform import Rotation as R

hom_matrix_lh2robot = """
-0.91787392  0.03214808  0.39556789 1231.7869873
  0.39598042  0.00740866  0.91822904 1607.19287109
  0.02658867  0.99945563 -0.01953023  1319.4855957
     0 0 0 1
         """
# hom_matrix_lh2robot = """
# 0.77346522  0.00770368  0.62936926 1177.82617188
# 0.62818998  0.01633672 -0.77749538 -1268.35327148
# -0.01625502  0.99128187 -0.00457333 1201.78857422
# 0 0 0 1
# """
hom_matrix_LH_Robo = np.ndarray = np.fromstring(hom_matrix_lh2robot,
                                                dtype=float,
                                                sep=" ").reshape((4, 4))


waypoint_matrix = """
0.16607491 -0.53677225 -1.88800999  0.6213734   0.59419598 -0.37261992
  0.34924167
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
    angles = euler.as_euler('xyz', degrees=True)
    return t, angles


t, angles = get_pos_rot_in_kuka_kos(target, hom_matrix_LH_Robo)

print(f"{t=}   {angles=}")
