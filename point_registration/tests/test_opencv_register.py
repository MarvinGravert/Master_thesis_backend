import pytest

import numpy as np
from scipy.spatial.transform import Rotation as R

from modules.algorithms.opencv import OpencvAlgorithm


class TestOpenCVPointRegister():
    @pytest.mark.parametrize(
        "hom_matrix",
        [pytest.lazy_fixture("hom_matrix_random"),
         pytest.lazy_fixture("unity_hom_matrix"),
         #  pytest.lazy_fixture("hom_matrix_1"),
         #  pytest.lazy_fixture("hom_matrix_mirror"),
         #  pytest.lazy_fixture("hom_matrix_mirror_2")
         ]
    )
    def test_simple_register(self,
                             opencv_register: OpencvAlgorithm,
                             base_point_list: np.ndarray,
                             hom_matrix: np.ndarray):

        p_set_2 = [hom_matrix@np.append(vec, 1) for vec in base_point_list]
        p_set_2 = np.array(p_set_2)[:, :3]
        T = opencv_register.register_point_set(point_set_1=base_point_list,
                                               point_set_2=np.array(p_set_2))

        assert np.isclose(a=hom_matrix,
                          b=T).all()

    def test_simple_register_negativ(self,
                                     base_point_list: np.ndarray,
                                     simple_transformation: np.ndarray):

        t = OpencvAlgorithm(ransac_parameters=None)
        T = t.register_point_set(point_set_1=base_point_list,
                                 point_set_2=base_point_list,)
        assert not np.isclose(a=simple_transformation,
                              b=T[:3, :3]).all()
