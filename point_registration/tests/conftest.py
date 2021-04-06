import pytest
import numpy as np
from scipy.stats import special_ortho_group

from point_set_registration_pb2 import RANSACParameters

from modules.algorithms.kabsch import KabschAlgorithm
from modules.algorithms.opencv import OpencvAlgorithm


@pytest.fixture
def base_point_list():
    np.random.seed(0)
    return np.random.random((20, 3))


@pytest.fixture
def simple_transformation():
    return np.array((
        (1, 0, 0),
        (0, 0, 1),
        (0, -1, 0)
    ))


@pytest.fixture
def unity_hom_matrix():
    return np.array((
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1)
    ))


@pytest.fixture
def hom_matrix_1():
    return np.array((
        (1, 0, 0, 0),
        (0, 0, 1, 1),
        (0, -1, 0, 10),
        (0, 0, 0, 1)
    ))


@pytest.fixture
def hom_matrix_mirror():
    return np.array((
        (1, 0, 0, 10),
        (0, -1, 0, 0),
        (0, 0, -1, 20),
        (0, 0, 0, 1)
    ))


@pytest.fixture
def hom_matrix_mirror_2():
    return np.array((
        (-1, 0, 0, 10),
        (0, 0, 1, 0),
        (0, 1, 0, 20),
        (0, 0, 0, 1)
    ))


@pytest.fixture
def hom_matrix_random():
    R = special_ortho_group.rvs(3)
    t = np.random.random((3, 1))
    temp = np.hstack((R, t))
    return np.vstack((temp, [0, 0, 0, 1]))


@pytest.fixture
def arun_register():
    return KabschAlgorithm()


@pytest.fixture
def opencv_register():
    return OpencvAlgorithm(ransac_parameters=None)
