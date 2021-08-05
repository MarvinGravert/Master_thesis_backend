from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np
import matplotlib.pyplot as plt

from more_itertools import chunked
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.utf8')


def plot_cumultive_distribution(data_points: List[float], relevant_data: float):
    print(data_points)
    print(relevant_data)
    total = np.append(data_points, relevant_data)
    n = len(total)
    x = np.sort(total)
    y = np.arange(n)/n
    highlighted_x = np.where(x == relevant_data)
    highlighted_y = y[highlighted_x]
    n_red = len(data_points)
    x_red = np.sort(data_points)
    y_red = np.arange(n_red)/n_red
    print(np.mean(total))
    print(np.max(total))
    print(np.std(total))
    acc = round(np.mean(total), 2)
    std = round(np.std(total), 2)
    minVal = round(min(total), 2)
    maxVal = round(max(total), 2)
    # plotting
    plt.figure(dpi=200)
    # popt, pcov = curve_fit(func, x, y)
    plt.xlabel('Mittleres Abstandsquadrat [mm]', fontsize=15)
    plt.ylabel('Kumulative Häufigkeit', fontsize=15)

    # Min: {minVal:n}mm Max: {maxVal:n}mm
    plt.title('Roboter-Referenzierung RMSE:\n'+f'{acc:n}mm\u00B1{std:n}mm', fontsize=15)
    # TODO: check naming kumulativer Fehler, evtl Verteilungsfunktion? siehe Normalverteilung
    print(len(x))
    plt.scatter(x_red, y_red, marker='o')
    plt.scatter(relevant_data, y=highlighted_y)
    # plt.plot(x, func(x, *popt), 'r-', label="Fitted Curve")
    plt.grid()
    # ticks
    ticky = list()
    for ti in chunked(x, 13):
        ticky.append(round(np.mean(ti), 0))
    # ticky = [20, 50, 80]
    # plt.xticks(np.linspace(start=min(x), stop=max(x), num=20, dtype=int))
    # accuracy line
    plt.vlines(acc, ymin=0, ymax=2, colors="r")
    ticky.append(acc)
    plt.ticklabel_format(useLocale=True)
    # add stuff
    # plt.xticks(ticky)
    plt.ylim(ymin=0, ymax=1.05)
    plt.xlim(xmin=0)
    plt.show()


def get_register_data():
    basepath = Path("./overall_acc_data")
    path2file = basepath/Path("point_registering_data.txt")
    return np.genfromtxt(path2file, delimiter=",", skip_header=1)


def cumultive_plot_main():
    data = get_register_data()  # rmse, mae, max, std

    # get used data
    cali_data = data[-2, :]
    reduced = np.delete(data, (-2), axis=0)
    plot_cumultive_distribution(
        data_points=reduced[:, 0],
        relevant_data=cali_data[0])


if __name__ == "__main__":
    cumultive_plot_main()
