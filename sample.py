from pyBvh.bvh import bvh
from pyBvh.node import ntype

import numpy as np
import sys, time

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.animation as animation

if __name__ == "__main__":
    mocap = bvh("test.bvh")
    mocap.print_tree()
    num_nodes = mocap.get_num_nodes()
    num_frm = mocap.get_num_frames()

    start = time.time()
    for m in mocap:
        roots = m[ntype.ROOT]
    duration = time.time() - start
    print('{0} frame : decode time {1} : fps = {2}'.format(num_frm, duration, num_frm / duration))
# animation 
    X = np.zeros(num_nodes, dtype=np.float32)
    Y = np.zeros(num_nodes, dtype=np.float32)
    Z = np.zeros(num_nodes, dtype=np.float32)

    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')

    def anim(frame):
        bone = mocap[frame]
        for i, n in enumerate(bone):
            pos = n.global_matrix.getTranslate()
            X[i] = pos.x() * 10.0
            Z[i] = pos.y() * 10.0
            Y[i] = pos.z() * 10.0
        plt.cla()
        cent = bone[ntype.ROOT][0].global_matrix.getTranslate()
        ax.set_xlim(cent.x() - 100, cent.x() + 100)
        ax.set_ylim(cent.z() - 100, cent.z() + 100)
        ax.set_zlim(cent.y(), cent.y() + 200)
        ax.scatter(X, Y, Z)
 
    anime = animation.FuncAnimation(
        fig, anim,
        interval=1,
        frames=np.arange(1, 600),
        repeat=True,
    )

    plt.show()
