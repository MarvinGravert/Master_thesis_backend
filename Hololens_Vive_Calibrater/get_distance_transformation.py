import numpy as np
from backend_utils.linear_algebra_helper import get_angle_from_rot_matrix, combine_to_homogeneous_matrix
from scipy.spatial.transform import Rotation as R

start_pos = np.array([1, 1, 0])
start_quat = np.array([0, 0, 0, 1])

end_pos = np.array([1, 1, 0])
end_quat = np.array([0, 0, 0, 1])

rStart = R.from_quat(start_quat)
rEnd = R.from_quat(end_quat)
start_matrix = combine_to_homogeneous_matrix(rotation_matrix=rStart.as_matrix(),
                                             translation_vector=start_pos)

end_matrix = combine_to_homogeneous_matrix(rotation_matrix=rEnd.as_matrix(),
                                           translation_vector=end_pos)

correction_matrix = np.linalg.inv(end_matrix)@start_matrix

error_vec = correction_matrix[:3, 3]
error_rot_matrix = correction_matrix[:3, :3]

error_angle = get_angle_from_rot_matrix(error_rot_matrix)
error_mag = np.linalg.norm(error_vec)

print(f"{error_angle=}")
print(f"{error_mag=}")
