from read_file import get_robot_endeff_lh_kos, get_robot_endeff_rob_kos
import numpy as np
from numpy import linalg
from scipy.spatial.transform import Rotation as R
from backend_utils.linear_algebra_helper import combine_to_homogeneous_matrix, separate_from_homogeneous_matrix
# pos = np.array([-0.37501809000968933, -0.28728243708610535, -1.9975359439849854])*1000
# quat = [0.07808689141656913, 0.8429020124305449, 0.5151832183445801, -0.1341411697029631]
pos = np.array([-0.16714711487293243, -0.44377046823501587, -1.9826704263687134])*1000
quat = [0.07528809607110072, 0.84214767582106, 0.5170650616255202, -0.13322735012588585]
w, i, j, k = quat

rotTracker2LH = R.from_quat([i, j, k, w])

rotTracker2LH = rotTracker2LH.as_matrix()
hom_matrix_tracker2LH = combine_to_homogeneous_matrix(rotTracker2LH, pos)

# print(hom_matrix)
# print(np.linalg.inv(hom_matrix_tracker2LH)[:3, 3]/1000)

# robPos = [-0.00835, -112.71, 903.50]
# robABC = [-18.21, 42.29, 69.58]
robPos = [181.45, -174.34, 724.19]
robABC = [-18.2, 42.29, 69.59]
rot_rob = R.from_euler('zyx', robABC, degrees=True)

rot_base2eff = rot_rob.as_matrix()
# print(rot_base2eff)
rot_eff2base = np.linalg.inv(rot_base2eff)
# print(rot_eff2base)
hom_eff2base = combine_to_homogeneous_matrix(rot_eff2base, np.array(robPos))
# print(hom_eff2base)

# test_r = R.from_matrix(rot_eff2base)
# print(test_r.as_euler('xyz', degrees=True))

tracker2Endeffektor = """
0 1 0 0
1 0 0 0 
0 0 -1 80
0 0 0 1
"""
tracker2Endeffektor = np.fromstring(tracker2Endeffektor, dtype=float, sep=" ").reshape((4, 4))

hom_lh2base = hom_eff2base@tracker2Endeffektor@np.linalg.inv(hom_matrix_tracker2LH)

# print(np.linalg.inv(hom_lh2base))

flange_point = hom_matrix_tracker2LH@np.array([0, 0, 80, 1])

# print(hom_lh2base@flange_point)
# print(hom_lh2base)


test_lh2base = """ 
7.62121055e-01 -4.50340650e-02 -6.45866419e-01 -1.05854797e+03
5.53546789e-01 5.62720560e-01 6.13947493e-01 1.54827075e+03
3.35793761e-01 -8.25419593e-01 4.53789648e-01 1.71940913e+03
0 0 0 1
"""
test_lh2base = np.fromstring(test_lh2base, dtype=float, sep=" ").reshape((4, 4))

# print(hom_lh2base-test_lh2base)


rot, trans = separate_from_homogeneous_matrix(hom_lh2base-test_lh2base)

# print(get_angle_from_rot_matrix(rot))

test_t = test_lh2base@flange_point
# print(test_lh2base@flange_point)
# print(test_t-flange_point)
# print(np.linalg.norm(test_t[:3]-robPos))

flange_point = np.array([0, 0, 80, 1])
p1 = """
-0.3709145784378052 -0.133503720164299 -0.9190208911895752 0.10056761652231216 
0.38203132152557373 -0.923933744430542 -0.019969480112195015 -0.7210052609443665 
-0.8464482426643372 -0.35850170254707336 0.393702894449234 -2.6030077934265137
0 0 0 1
"""
hom_tracker2lh_p1 = np.fromstring(p1, dtype=float, sep=" ").reshape((4, 4))
hom_tracker2lh_p1[:3, 3] = hom_tracker2lh_p1[:3, 3]*1000
p1 = hom_tracker2lh_p1@flange_point
print(p1)
# print(hom_tracker2lh_p1)
p14 = """
-0.24830128252506256 0.6658034324645996 -0.7035993933677673 0.1457667350769043 
0.06488673388957977 -0.7132832407951355 -0.6978657245635986 -0.5645045638084412 
-0.9665071368217468 -0.2189352661371231 0.13390742242336273 -2.281865358352661
0 0 0 1
"""
hom_tracker2lh_p14 = np.fromstring(p14, dtype=float, sep=" ").reshape((4, 4))
hom_tracker2lh_p14[:3, 3] = hom_tracker2lh_p14[:3, 3]*1000
# print(hom_tracker2lh_p6)

point_list_1 = get_robot_endeff_lh_kos("20210728", 6, 80)
point_list_2 = get_robot_endeff_rob_kos(file_name="20210728_CalibrationSet_2")
p1 = point_list_1[0, :]
p1_rob = point_list_2[0, :]
list_dist_err = list()
for point_lh, point_rob in zip(point_list_1, point_list_2):
    ref_lh = p1-point_lh
    ref_rob = p1_rob-point_rob
    dist_lh = np.linalg.norm(ref_lh)
    dist_rob = np.linalg.norm(ref_rob)
    list_dist_err.append(np.abs(dist_lh-dist_rob))
    print(f"LH: {dist_lh}   Rob: {dist_rob}  Diff: {np.abs(dist_lh-dist_rob)}")

# print(np.mean(list_dist_err))
t1 = [0.19295401, -0.8822137,  -1.69967003]
t2 = [0.3392577, -0.88732084, -1.73324133]
t3 = [0.48485993, -0.89233955, -1.7650888]
t4 = [0.19312828, - 0.88217493, - 1.7003798]  # t1 again
t5 = [0.33927349, -0.88726266, -1.73328096]  # t2 again
base_point = np.array(t1)
test_point = np.array(t5)
tdiff = base_point-test_point
# print(np.linalg.norm(tdiff)*1000)
rob1 = np.array([557.81, -537.79, 410.3])
rob2 = np.array([705.74, -520.09, 410.34])
rob3 = np.array([408.58, -540.65, 408.24])
rob4 = np.array([261.08, -544.82, 409.14])

print(np.linalg.norm(rob1-rob2))
print(np.linalg.norm(rob1-rob3))
print(np.linalg.norm(rob1-rob4))
print(np.linalg.norm(rob2-rob4))
