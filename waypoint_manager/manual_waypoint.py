from backend_api.general import InterpolationType, Waypoint
from backend_utils.averageQuaternion import averageQuaternions
from backend_api.general import InterpolationType
from backend_utils.linear_algebra_helper import separate_from_homogeneous_matrix
import numpy as np
from scipy.spatial.transform import Rotation as R

hom_matrix_lh2robot = """
    0.77452248  0.01779656  0.63229603 1189.11499023
    0.63231397  0.00531408 -0.77469403 -1272.83557129
    -0.01714696  0.9998275  -0.00713714 1205.47021484
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
0.35851979 -0.60233247 -1.37997055  0.71165089  0.662407    0.18081498 -0.14857095
0.36067755 -0.60197859 -1.37912985  0.70778262  0.66455595  0.18011435 -0.15800904
0.35981989 -0.60244846 -1.37230483  0.69610235  0.67966354  0.17849034 -0.14709623
0.35964191 -0.60286862 -1.37343518  0.69805448  0.67826323  0.17745402 -0.14556274
0.36019615 -0.60279196 -1.37688909  0.70127833  0.67151669  0.18256854 -0.15473011
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
