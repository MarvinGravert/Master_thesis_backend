from typing import List, Tuple
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as R
from more_itertools import grouper
from scipy import stats
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cmx
import matplotlib as mpl

from backend_utils.linear_algebra_helper import build_coordinate_system_via_3_points
robo_data = """
442.60 298.69 426.56 109.76 80.69 100.43
505.68 214.48 533.05 109.76 80.69 100.43
434.65 233.41 588.10 14.99 42.90 15.68
534.56 -41.27 429.35 -9.11 56.21 -16.75
485.98 89.69 670.9 -13.07 45.09 -4.75
134.86 263.18 595.28 -49.56 76.50 -42.58
110.78 249.64 436.79 -101.63 76.40 -109.12
168.27 -227.34 460.13 -72.63 54.81 -66.31
612.76 -249.98 466.02 0.52 52.44 -21.31
266.06 -45.33 849.72 -68.47 8.77 -5.80
256.22 -240.53 625.65 -21.67 60.90 -26.42
462.65 -251.92 544.62 51.49 38.60 48.19
354.08 160.88 704.34 -62.54 78.74 -60.61
463.22 10.85 605.96 -12.54 45.15 -5.94
250.96 -17.32 597.60 -12.55 45.16 -5.95
250.96 209.55 597.60 -12.55 45.16 -5.95
371.48 -184.19 508.73 -13.68 52.31 -6.00
665.32 -14.34 583.70 -33.03 40.78 -4.80
233.83 97.92 718.85 70.83 46.55 34.05
353.71 187.52 592.06 91.24 25.03 76.01
377.28 -105.08 608.19 46.89 23.70 73.68
"""
robo_data = np.fromstring(robo_data, dtype=float, sep=' ').reshape((-1, 6))
robo_data = robo_data[:, :3]


def get_data_base_path() -> Path:
    return Path("./overall_acc_data")


def read_laser_data(path2file: Path) -> np.ndarray:
    return np.genfromtxt(path2file, delimiter=",", skip_header=1)


def get_laser_data(date: str, experiment_number: int) -> np.ndarray:
    """returns the raw laser data taken from X experiment on the specified date

    Args:
        date (str): yyyymmdd format
        experiment_number (int): number of experiment

    Returns:
        np.ndarray: nx24 See the raw file to see the column specification
    """
    data_dir = get_data_base_path()
    path2laser_file = data_dir/Path(f"{date}_Exp{experiment_number}.txt")
    return read_laser_data(path2laser_file)


def pre_process_laser_data(laser_data: np.ndarray) -> np.ndarray:
    """cut the laser data down and check if anything has moved during the measuring circles


    Args:
        laser_data (np.ndarray): nx24 array

    Returns:
        np.ndarray: nx3 array
    """
    laser_data = laser_data[:, :3]
    """
    CHECKING If MOVED
    Workign in 4point cycles means 0->3 4->7 etc shuold be same location
    """
    # TODO: Implement x)
    return laser_data


def process_laser_data(laser_data: np.ndarray) -> List[np.ndarray]:
    """receives laser data and processes it into hom_matrix
    representing the transformation to the laser tracker center

    Args:
        laser_data (np.ndarray): [description]
    """
    hom_matrix_list = list()
    for origin, x_axis, y_axis, _ in grouper(laser_data, 4):
        hom_point2laser = build_coordinate_system_via_3_points(
            origin=origin,
            x_axis_point=x_axis,
            y_axis_point=y_axis
        )
        hom_matrix_list.append(hom_point2laser)
    return hom_matrix_list


def calculate_distance_points(date: str, exp_num: int):
    """function that calculates the avg distance between the target point on the
    tripod mounted plate and the robot tcp in the laser tracker reference system

    Args:
        date (str): date of exp
        exp_num (int): nump of exp on that date
    """
    # tip of tcp in roboter_laser_kos
    tcp_tip = np.array([51, 51, 93-10, 1])
    # target location for waypoint
    target_loc = np.array([132, 132, -10, 1])

    laser_data = get_laser_data(date, experiment_number=exp_num)
    laser_data = pre_process_laser_data(laser_data)
    # print(laser_data)
    list_hom_matrix = process_laser_data(laser_data)

    distance_list = list()
    for hom_target2laser, hom_rob2laser in grouper(list_hom_matrix, 2):
        # target shuold be first
        target_in_laser = hom_target2laser@target_loc
        tcp_tip_in_laser = hom_rob2laser@tcp_tip

        dist = np.linalg.norm(target_in_laser-tcp_tip_in_laser)
        distance_list.append(dist)

    # print(distance_list)
    # print(len(distance_list))
    # print(f"{np.mean(distance_list)} \u00B1 {np.std(distance_list)}")
    # print(stats.ttest_1samp(distance_list, 0))
    plot_waypoint_error(distance_list)
    # print(np.mean(distance_list))
    # print(np.std(distance_list, ddof=1))
    # print(max(distance_list))
    # test = np.array(distance_list)
    # test = test**2
    # print(np.sqrt(np.mean(test)))


def calculate_axis_distance(date: str, exp_num: int):
    # tip of tcp in roboter_laser_kos
    tcp_tip = np.array([51, 51, 93-10, 1])
    # target location for waypoint
    target_loc = np.array([132, 132, -10, 1])

    # acquire transformation data alternating tripod-robot-tripod-robot
    laser_data = get_laser_data(date, experiment_number=exp_num)
    laser_data = pre_process_laser_data(laser_data)
    list_hom_matrix = process_laser_data(laser_data)

    # we want the axis distance from tcp point to tripod coordiante system
    # hence build robot-kos->tripod-kos hom matrix
    err_vec_list = list()
    for hom_target2laser, hom_rob2laser in grouper(list_hom_matrix, 2):
        hom_rob2target = np.linalg.inv(hom_target2laser)@hom_rob2laser
        tcp_in_target = hom_rob2target@tcp_tip
        # get the error vector from target to tcp
        err_vec = tcp_in_target-target_loc
        err_vec_list.append(err_vec)

    overall_err_vec_matrix = np.array(err_vec_list)[:3]
    print(np.mean(overall_err_vec_matrix, 0))
    print(np.std(overall_err_vec_matrix, 0))
    # print(stats.kstest(overall_err_vec_matrix[:, 1], "norm"))
    # print(stats.ttest_1samp(overall_err_vec_matrix[:, 2], 0))
    del err_vec_list[3]
    test = np.array(err_vec_list)[:3]
    print(len(err_vec_list))
    # print(stats.ttest_1samp(test[:, 2], 0))
    ##
    axis = overall_err_vec_matrix[:, 2]
    test = np.array(axis)
    test = test**2
    print(np.sqrt(np.mean(test)))
    print(np.mean(axis))
    print(max(np.abs(axis)))
    print(np.std(axis, ddof=1))
    print(stats.ttest_1samp(axis, 0))


def get_std_data():
    basepath = get_data_base_path()
    path2file = basepath/Path("placement_files/test_mean_position.txt")
    return np.genfromtxt(path2file, delimiter=" ", skip_header=1)


def get_user_placement_error():
    """calcuatates the std in placeing the waypoitn with th econtroller (human induced error)
    pritns it in the robot coordinate system to have some relevancey
    """
    data = get_std_data()
    std_list = list()
    for data_set in grouper(data, 5):
        temp = np.std(data_set, 0)
        std_list.append(temp)
    meany = np.mean(np.array(std_list), 0)
    print(meany)
    hom_lh2rob = """
    -0.91397965  0.0060312   0.40571517 1240.45629883
    0.40575796  0.01674379  0.91382718 1613.12597656
    -0.00128174  0.99984163 -0.01775069 1295.75524902
    0 0 0 1
    """
    hom_lh2rob = """
    -0.91397965  0.0060312   0.40571517
    0.40575796  0.01674379  0.91382718
    -0.00128174  0.99984163 -0.01775069

    """
    hom_lh2rob = np.fromstring(hom_lh2rob, dtype=float, sep=" ").reshape((3, 3))
    # print(hom_lh2rob@)
    print(hom_lh2rob@meany[:3])


def get_user_hand_jitter():
    basepath = get_data_base_path()
    path2file = basepath/Path("placement_files/placement_position_std.txt")
    data = np.genfromtxt(path2file, delimiter=" ", skip_header=1)
    print(np.mean(data, 0))
    meany = np.mean(data, 0)
    print(np.linalg.norm(meany[:3]))


def plot_waypoint_error(error_list: List[float]):
    """plots teh position of the waypoint in robot kos. Their size depends on the
    value in the given list

    Args:
        error_list (List[float]): placement error magnitude at the waypoint
    """
    basepath = get_data_base_path()
    path2file = basepath/Path("placement_files/robot_waypoint_pos.txt")
    data = np.genfromtxt(path2file, delimiter=",", skip_header=1)
    from matplotlib.ticker import StrMethodFormatter, ScalarFormatter
    import locale
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
    mpl.rcParams['axes.formatter.use_locale'] = True
    fig = plt.figure(figsize=(4, 4))

    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel("x [mm]", fontsize=15)

    ax.set_ylabel("y [mm]", fontsize=15)
    import upsidedown
    test = upsidedown.transform('z [mm]')
    ax.set_zlabel(test, fontsize=15)
    scatter = ax.scatter(
        xs=data[:, 0],
        ys=data[:, 1],
        zs=data[:, 2],
        s=0.1 * (np.array(error_list)*3)**2)

    # print(error_list)
    # print(0.1 * (np.array(error_list)*3)**2)
    kw = dict(prop="sizes", num=3, color=scatter.cmap(0.35),
              #   fmt="{x:f}",
              func=lambda s: np.sqrt(s / 0.1) / 3)
    handles, labels = scatter.legend_elements(**kw)
    labels = ['$\\mathdefault{3,94 mm}$',
              '$\\mathdefault{10,42 mm}$', '$\\mathdefault{15,55 mm}$']
    legend2 = ax.legend(handles, labels,
                        loc="right", prop={'size': 15})
    # print(scatter.legend_elements(**kw))
    ax.add_artist(legend2)
    # plt.title("Abweichung zwischen angezielten \nund angefahrenen Wegpunkt")
    # ax.set_title('Abweichung zwischen angezielten \nund angefahrenen Wegpunkt', y=1.0, pad=-34)

    min = np.amin(robo_data, axis=0)
    max = np.amax(robo_data, axis=0)
    # BUILD CUBE
    center = min+(max-min)/2
    size = max-min+[20, 20, 20]
    # https://stackoverflow.com/questions/30715083/python-plotting-a-wireframe-3d-cuboid

    ox, oy, oz = center
    l, w, h = size

    x = np.linspace(ox-l/2, ox+l/2, num=2)
    y = np.linspace(oy-w/2, oy+w/2, num=2)
    z = np.linspace(oz-h/2, oz+h/2, num=2)
    x1, z1 = np.meshgrid(x, z)
    y11 = np.ones_like(x1)*(oy-w/2)
    y12 = np.ones_like(x1)*(oy+w/2)
    x2, y2 = np.meshgrid(x, y)
    z21 = np.ones_like(x2)*(oz-h/2)
    z22 = np.ones_like(x2)*(oz+h/2)
    y3, z3 = np.meshgrid(y, z)
    x31 = np.ones_like(y3)*(ox-l/2)
    x32 = np.ones_like(y3)*(ox+l/2)

    ax = fig.gca(projection='3d')
    # outside surface
    ax.plot_wireframe(x1, y11, z1, color='b', rstride=1, cstride=1, alpha=0.6)
    # inside surface
    ax.plot_wireframe(x1, y12, z1, color='b', rstride=1, cstride=1, alpha=0.6)
    # bottom surface
    ax.plot_wireframe(x2, y2, z21, color='b', rstride=1, cstride=1, alpha=0.6)
    # upper surface
    ax.plot_wireframe(x2, y2, z22, color='b', rstride=1, cstride=1, alpha=0.6)
    # left surface
    ax.plot_wireframe(x31, y3, z3, color='b', rstride=1, cstride=1, alpha=0.6)
    # right surface
    ax.plot_wireframe(x32, y3, z3, color='b', rstride=1, cstride=1, alpha=0.6)

    plt.xticks([100, 300, 500, 700])  # Set label locations.
    plt.show()


if __name__ == "__main__":
    date = "20210731"
    exp_num = 1
    calculate_distance_points(date, exp_num)
    # calculate_axis_distance(date, exp_num)
    # get_user_placement_error()
    # get_user_hand_jitter()
