
import pytest

import numpy as np
from scipy.spatial.transform import Rotation as R

from backend_utils.linear_algebra_helper import separate_from_homogeneous_matrix

from utils.check_cost_function import check_cost_function


class TestReprojectionError():

    @pytest.mark.parametrize(
        "hom_matrix",
        [pytest.lazy_fixture("unity_hom_matrix"), ]
    )
    def test_hom_matrix_register(self,
                                 base_point_list: np.ndarray,
                                 hom_matrix: np.ndarray):

        R, t = separate_from_homogeneous_matrix(homogenous_matrix=hom_matrix)
        assert np.isclose(check_cost_function(point_set_1=base_point_list,
                                              point_set_2=base_point_list,
                                              R=R,
                                              t=t), 0)
