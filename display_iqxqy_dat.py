#!/usr/bin/env python
from __future__ import print_function


import sys
import os

import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl

mpl.rcParams['image.cmap'] = 'viridis'


def parse_file_into_1d_array(filepath):
    data = np.genfromtxt(filepath, skip_header=2, names="qx, qy, iqxqy, err")
    qx, qy, iqxqy, err = data['qx'], data['qy'], data['iqxqy'], data['err']
    return qx, qy, iqxqy, err

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} *Iqxy.dat".format(sys.argv[0]))
        sys.exit(-1)
    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print("{} is not a file.".format(filepath))
        sys.exit(-1)
    qx, qy, iqxqy, _ = parse_file_into_1d_array(sys.argv[1])
    plt.figure()
    plt.title("Logarithm: {}".format(os.path.basename(filepath)))
    plt.scatter(qx, qy, c=np.log(iqxqy), s=50, edgecolor='', marker='s')
    plt.colorbar()
    plt.show()
