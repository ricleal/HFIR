#!/usr/bin/env python
from __future__ import print_function


import sys
import os
import math

import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
from collections import Counter

mpl.rcParams['image.cmap'] = 'viridis'


def plot(x, y, z, title):

    plt.figure()
    plt.title("Logarithm: {}".format(title))
    plt.scatter(qx, qy, c=np.log(iqxqy), s=50, edgecolor='', marker='s')
    plt.colorbar()
    plt.show()

def parse_file_into_1d_array(filepath):
    data = np.genfromtxt(filepath, skip_header=2, names="qx, qy, iqxqy, err")
    qx, qy, iqxqy, err = data['qx'], data['qy'], data['iqxqy'], data['err']
    return qx, qy, iqxqy, err

def transform_in_regular_matrix(qx, qy, iqxqy, err):
    qx_unique = np.unique(qx)
    qy_unique = np.unique(qy)

    step_x = np.round(np.absolute(np.ediff1d(qx)), 6)
    step_y = np.round(np.absolute(np.ediff1d(qy)), 4)

    step_x_ocurrences = Counter(step_x)
    step_y_ocurrences = Counter(step_y)

    step_x_most_common_values = step_x_ocurrences.most_common()
    step_y_most_common_values = step_y_ocurrences.most_common()

    step_x_most_common = step_x_most_common_values[0][0] if step_x_most_common_values[0][0] != 0 else step_x_most_common_values[1][0]
    step_y_most_common = step_y_most_common_values[0][0] if step_y_most_common_values[0][0] != 0 else step_y_most_common_values[1][0]

    print("Steps X and Y:")    
    print(step_x_most_common)
    print(step_y_most_common)

    step_x = step_x_most_common
    step_y = step_y_most_common

    # Create mesh array
    x_space = np.linspace(qx.min(), qx.max(), math.floor((qx.max() - qx.min()) / step_x_most_common))
    y_space = np.linspace(qy.min(), qy.max(), math.floor((qy.max() - qy.min()) / step_y_most_common))
    xv, yv = np.meshgrid(x_space, y_space)


    z = [], e = []
    x = qx.min()
    y = qy.min()
    data_index = 0

    while x <= qx.max() and y <= qy.max():
        

        # TODO


        x += step_x
        y += step_y
    









if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} *Iqxy.dat".format(sys.argv[0]))
        sys.exit(-1)
    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print("{} is not a file.".format(filepath))
        sys.exit(-1)
    qx, qy, iqxqy, err = parse_file_into_1d_array(sys.argv[1])
    #plot(qx, qy, iqxqy, os.path.basename(filepath))
    transform_in_regular_matrix(qx, qy, iqxqy, err)

