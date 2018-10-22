#!/usr/bin/env python3

import sys
import numpy as np
import xml.etree.ElementTree as ET
import logging
import glob
import matplotlib.pyplot as plt
import os

logging.getLogger("matplotlib").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def process(filename, xpath="Data/Detector"):

    logger.info("Parsing: %s." % filename)
    tree = ET.parse(filename)
    root = tree.getroot()

    def getMetadata(xpath):
        '''
        Given Xpath returns either float or string
        '''
        elems = root.findall(xpath)
        if not elems:
            logger.error("xpath %s is not valid!" % xpath)
            return None
        elif len(elems) > 1:
            logger.warning("xpath %s has more than one element (len = %d)! Returning first!" % (
                xpath, len(elems)))
        value_as_string = elems[0].text
        try:
            return float(value_as_string)
        except ValueError:
            return value_as_string

    def getData(xpath):
        '''
        Parses the XML xpath data into a 2D Xarray
        '''
        data_str = getMetadata(xpath)
        data_list_of_chars = [line.split("\t")
                              for line in data_str.strip().split("\n")]
        data = [list(map(int, line)) for line in data_list_of_chars]
        data_np = np.array(data)
        data_np = np.rot90(data_np)
        data_np = np.flipud(data_np)
        return data_np

    data = getData(xpath)
    return data


def show_detector(filename):
    data = process(filename, xpath="Data/Detector")
    fig, ax = plt.subplots()
    im = ax.pcolormesh(data)
    fig.colorbar(im, ax=ax)
    ax.set_title(os.path.basename(filename))
    ax.set_xlabel('Tube')
    ax.set_ylabel('Pixel')
    plt.show()


def show_tube(filename, tube=0):

    def smooth(y, box_pts):
        box = np.ones(box_pts)/box_pts
        y_smooth = np.convolve(y, box, mode='same')
        return y_smooth

    x = np.linspace(-0.54825, 0.54825, 256)  
    dx = -0.54825 # Step in mm of every pixel
    data = process(filename, xpath="Data/Detector")
    tube_to_plot = data[:, tube]
    derivative = np.diff(tube_to_plot)/dx
    tube_smooth = smooth(tube_to_plot, 10)
    derivative_smooth = np.diff(tube_smooth)/dx

    fig, ax = plt.subplots()

    ax.plot(tube_to_plot, label="Tube")
    ax.plot(derivative, label="Derivative")
    ax.plot(tube_smooth,  label="Smooth")
    ax.plot(derivative_smooth, label="Derivative Smooth")
    
    ax.set_title(os.path.basename(filename))
    ax.set_xlabel('Counts')
    ax.set_ylabel('Pixel')
    ax.grid(True)
    ax.legend()
    plt.show()


if __name__ == '__main__':

    if len(sys.argv) >= 2:
        files = glob.glob(sys.argv[1])
        for filename in files:
            # show_detector(filename)
            show_tube(filename)
    else:
        print('Use: %s <HFIR XML file pattern>' % sys.argv[0])
