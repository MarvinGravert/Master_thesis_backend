"""this module implements an function which takes a list of vr objects and averages their pose
"""
from typing import List

import numpy as np

from config.api_types import VRObject
from utils.averageQuaternion import averageQuaternions


def average_vr_pose(list_vr_object: List[VRObject]) -> VRObject:
    """loop over all the vr objects and average their pose
    for position simply mean averaging is used
    for rotation an acurate but computationally expensive alg is used to get a accurate solution

    retuns the first element of the list but with the pose set to the average
    """
    position_list = list()
    rotation_list = list()
    for vr_obj in list_vr_object:
        position_list.append(vr_obj.position)
        rotation_list.append(vr_obj.rotation)
    position_list = np.array(position_list)  # nx3 matrix
    rotation_list = np.array(rotation_list)  # nx4 matrix with w i j k
    avg_position = np.mean(position_list, axis=0)
    avg_rotation = averageQuaternions(Q=rotation_list)
    list_vr_object[0].rotation = avg_rotation.tolist()
    list_vr_object[0].position = avg_position.tolist()
    return list_vr_object[0]
