import pytest

import numpy as np

from backend_core.api.vr_objects import VRObject
from backend_utils.object_pose_averager import average_vr_pose


class TestPoseAverage():
    def test_same_object(self):
        vr_obj = VRObject(position=[0, 0, 1], rotation=[1, 0, 0, 0])
        test_list = 2*[vr_obj]
        result_obj = average_vr_pose(test_list)
        assert np.isclose(result_obj.rotation, vr_obj.rotation).all()
        assert np.isclose(result_obj.position, vr_obj.position).all()

    def test_mean_position(self):
        vr_obj_1 = VRObject(position=[1, 0, 0], rotation=[0, 1, 0, 1])
        vr_obj_2 = VRObject(position=[2, 0, 0], rotation=[0, 1, 0, 1])
        vr_obj_3 = VRObject(position=[3, 0, 0], rotation=[0, 1, 0, 1])
        test_list = [vr_obj_1, vr_obj_2, vr_obj_3]
        result_obj = average_vr_pose(test_list)
        assert np.isclose(vr_obj_2.position, result_obj.position).all()
