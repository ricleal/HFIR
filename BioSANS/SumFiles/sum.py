#!/usr/bin/env python

from __future__ import print_function

"""

Sums the counts for HFIR SANS xml files

Usage:

./sum.py -h
usage: sum.py [-h] [-o OUTPUT_FILE] files

Sum of HFIR SANS Files

positional arguments:
  files           Use Unix wildcars between quotes

optional arguments:
  -h, --help      show this help message and exit
  -o OUTPUT_FILE  Default: /Users/rhf/git/HFIR/BioSANS/out.xml


Example:
--------
./sum.py "Data/BioSANS_exp530_scan000*" -o /tmp/out.xml

"""

import argparse
import logging
import os
import sys
import xml.etree.ElementTree as ET
from glob import glob

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

xpaths_to_sum = [
    './Counters/time',
    './Counters/monitor',
    './Counters/detector',
    './Counters/detector_body',
    './Counters/detector_wing',
    './Data/Detector',
    './Data/DetectorWing',
]

def sum_file(filename, previous_root):
    
    logger.info("Parsing: %s", filename)
    
    tree = ET.parse(filename)
    root = tree.getroot()
    
    if previous_root is not None:
        for xpath in xpaths_to_sum:
            previous_elem = previous_root.find(xpath)
            elem = root.find(xpath)

            if 'Counters' in xpath:
                logger.info("Summing: %s. Previous: %s, This: %s", xpath, 
                    previous_elem.text, elem.text)
                elem.text = str(float(elem.text) + float(previous_elem.text))
                logger.info("New Value: %s = %s", xpath, elem.text)
            else:
                # Detectors
                new_lines = []
                logger.info("Parsing {}.".format(xpath))
                for p_line, line in zip(elem.text.splitlines(), previous_elem.text.splitlines()):
                    new_line = []
                    for p_i, i in zip(p_line.split(), line.split()):
                        new_line.append(float(p_i) + float(i))
                    new_lines.append(new_line)
                # Convert 2D array into a string
                elem.text = '\n'.join('\t'.join('%d' %x for x in y) for y in new_lines)
                elem.text += '\n'
    return root
        

def main():
    
    files = glob(args.files)
    if not files:
        logger.error("Nothing to do!")
        return
    
    root = None
    for file in files:
        root = sum_file(file, root)
    
    if root is not None:
        xmlstr = ET.tostring(root, encoding='UTF-8', method='xml')
        logger.info("Saving %s:", args.output_file)
        with open(args.output_file, "w") as f:
            f.write(xmlstr)

def parse_arguments():
    global args
    parser = argparse.ArgumentParser(
        description='Sum of HFIR SANS Files')
    
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "out.xml")
    parser.add_argument('-o', action="store", dest="output_file",
        default=output_file, help="Default: {}".format(output_file))
    parser.add_argument('files', help='Use Unix wildcars between quotes')

    args = parser.parse_args()
    

if __name__ == "__main__":
    parse_arguments()
    main()
