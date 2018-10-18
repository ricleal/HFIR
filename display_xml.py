#!/usr/bin/env python3

import sys
import numpy as np
import xml.etree.ElementTree as ET
import logging
import glob
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)



XPATH = "Data/Detector"


def show(filename):

    
    logger.info("Parsing: %s."%filename)
    tree = ET.parse(filename)
    root = tree.getroot()

    def getMetadata(xpath):
        '''
        Given Xpath returns either float or string
        '''
        elems = root.findall(xpath)
        if not elems:
            logger.error("xpath %s is not valid!"%xpath)
            return None
        elif len(elems) >1:
            logger.warning("xpath %s has more than one element (len = %d)! Returning first!"%(xpath,len(elems)))
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
        data_list_of_chars = [line.split("\t") for line in data_str.strip().split("\n")]
        data = [list(map(int, line)) for line in data_list_of_chars]
        data_np = np.array(data)
        data_np = np.rot90(data_np)
        data_np = np.flipud(data_np)
        return data_np


    data = getData(XPATH)
    plt.imshow(data)
    plt.show()


if __name__ == '__main__':

    if len(sys.argv) >= 2:
        files = glob.glob(sys.argv[1])
        for file in files:
            show(file)
    else:
        print('Use: %s <HFIR XML file pattern>' % sys.argv[0])