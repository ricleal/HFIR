#!/usr/bin/env python

"""

"""

import sys
import logging

from glob import glob
import xml.etree.ElementTree as ET

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
                for p_line, line in zip(elem.text.splitlines(), previous_elem.text.splitlines()):
                    new_line = []
                    for p_i, i in zip(p_line.split(), line.split()):
                        new_line.append(float(p_i) + float(i))
                    new_lines.append(new_line)
                # Convert 2D array into a string
                elem.text = '\n'.join('\t'.join('%d' %x for x in y) for y in new_lines)
    return root
        

def main():
    
    files = glob(sys.argv[1])
    if not files:
        logger.error("Nothing to do!")
        return
    
    root = None
    for file in files:
        root = sum_file(file, root)
    
    if root is not None:
        xmlstr = ET.tostring(root, encoding='utf8', method='xml')
        with open('/tmp/out.xml', "w") as f:
            f.write(xmlstr)
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Use {} <unix file wildcards>".format(sys.argv[0]))
        sys.exit(-1)
    main()
