from tests.conftest import opencv_register
import pytest

import numpy as np
from scipy.spatial.transform import Rotation as R

from modules.algorithms.kabsch import KabschAlgorithm


class TestArunPointRegister():

    @pytest.mark.parametrize(
        "hom_matrix",
        [pytest.lazy_fixture("hom_matrix_random"),
         pytest.lazy_fixture("unity_hom_matrix"),
         pytest.lazy_fixture("hom_matrix_1"),
         pytest.lazy_fixture("hom_matrix_mirror"),
         pytest.lazy_fixture("hom_matrix_mirror_2")]
    )
    def test_hom_matrix_register(self,
                                 arun_register: KabschAlgorithm,
                                 base_point_list: np.ndarray,
                                 hom_matrix: np.ndarray):

        p_set_2 = [hom_matrix@np.append(vec, 1) for vec in base_point_list]
        p_set_2 = np.array(p_set_2)[:, :3]
        T = arun_register.register_point_set(
            point_set_1=base_point_list,
            point_set_2=p_set_2)
        assert np.isclose(a=hom_matrix,
                          b=T).all()

    def test_simple_register_negativ(self,
                                     arun_register: KabschAlgorithm,
                                     base_point_list: np.ndarray,
                                     unity_hom_matrix: np.ndarray,
                                     hom_matrix_random: np.ndarray
                                     ):
        p_set_2 = [unity_hom_matrix@np.append(vec, 1) for vec in base_point_list]
        p_set_2 = np.array(p_set_2)[:, :3]
        T = arun_register.register_point_set(point_set_1=base_point_list,
                                             point_set_2=p_set_2)

        assert not np.isclose(a=hom_matrix_random,
                              b=T).all()
