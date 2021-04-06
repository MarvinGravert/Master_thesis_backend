"""this module implements an function which takes a list of vr objects and averages their pose
"""
from typing import List, Union

import numpy as np

from backend_api.vr_objects import VRObject, ViveController, ViveTracker
from backend_utils.averageQuaternion import averageQuaternions


def average_vr_pose(list_vr_object: List[Union[VRObject, ViveTracker, ViveController]]
                    ) -> Union[VRObject, ViveTracker, ViveController]:
    """loop over all the vr objects and average their pose
    for position simply mean averaging is used
    for rotation an acurate but computationally expensive alg is used to get a accurate solution

    Args:
        Union[VRObject, ViveTracker, ViveController]: 

    Returns:
        Union[VRObject, ViveTracker, ViveController]: the first object in the passed list of object but containing 
    """
    position_list = list()
    rotation_list = list()
    for vr_obj in list_vr_object:
        position_list.append(vr_obj.position)
        rotation_list.append(vr_obj.rotation)
    position_list = np.array(position_list)  # nx3 matrix
    rotation_list = np.array(rotation_list)  # nx4 matrix with w i j k
    """
        ----------
        Reading into Matrix done
        Start averaging
        ----------
    """
    avg_position = np.mean(position_list, axis=0)
    avg_rotation = averageQuaternions(Q=rotation_list)
    """
        ----------
        Write into Object
        ----------
    """
    list_vr_object[0].rotation = avg_rotation.tolist()
    list_vr_object[0].position = avg_position.tolist()
    return list_vr_object[0]
