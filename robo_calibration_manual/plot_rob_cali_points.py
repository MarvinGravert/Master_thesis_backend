import numpy as np
import matplotlib.pyplot as plt
from itertools import product, combinations
from mpl_toolkits.mplot3d import Axes3D


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

min = np.amin(robo_data, axis=0)
max = np.amax(robo_data, axis=0)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

for i, row in enumerate(robo_data):
    if i < 12:
        ax.scatter(row[0], row[1], row[2], c="g")
    else:
        ax.scatter(row[0], row[1], row[2], c="r")
    ax.text(row[0], row[1], row[2],  '%s' % (str(i+1)), size=10, zorder=1,  color='k')

ax.set_xlabel('X [mm]')
ax.set_ylabel('Y [mm]')
ax.set_zlabel('Z [mm]')

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

plt.show()
