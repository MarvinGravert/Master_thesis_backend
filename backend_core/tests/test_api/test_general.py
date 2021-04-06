import numpy as np
from scipy.spatial.transform import Rotation as R

from holoViveCom_pb2 import CalibrationInfo

from backend_api.general import Calibration


class TestCalibration:

    def test_correct_init_unity_matrix(self):
        expected = np.identity(4)
        assert (expected == Calibration().matrix).all()
        assert (expected == Calibration(calibration_matrix="""
                1 0 0 0
                0 1 0 0
                0 0 1 0
                0 0 0 1
                """).matrix).all()
        assert (expected == Calibration(
            calibration_matrix="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1").matrix).all()

    def test_correct_init_custom_matrix(self):
        test_matrix = np.arange(16).reshape(4, 4)
        assert (test_matrix == Calibration(calibration_matrix="""
                0 1 2 3 
                4 5 6 7 
                8 9 10 11
                12 13 14 15
                """).matrix).all()

    def test_set_calibration_via_grpc_object(self):
        test_matrix = np.random.random((4, 4))
        test_grpc_obj = CalibrationInfo(calibrationMatrixRowMajor=test_matrix.flatten())
        calibration_obj = Calibration()
        calibration_obj.set_calibration_via_grpc_object(calibration_info=test_grpc_obj)
        assert (np.isclose(test_matrix, calibration_obj.matrix)).all()

    def test_calibration_as_grpc_objet(self):
        test_matrix = np.arange(16)
        expected_grpc_obj = CalibrationInfo(calibrationMatrixRowMajor=test_matrix.flatten())

        actual_grpc_obj = Calibration(calibration_matrix=np.array2string(np.arange(16)).strip("[]"))
        assert expected_grpc_obj == actual_grpc_obj.get_calibration_as_grpc_object()
