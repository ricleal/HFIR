#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
./replace.py \
-x ./Motor_Positions/attenuator_pos[@pos] 1234 \
-x ./Header/Instrument Dummy \
data/HiResSANS_exp3_scan0011_0001.xml data/HiResSANS_exp3_scan0010_0001.xml


"""
from settings import logger, args, config

import sys
import glob
import os.path

import os, sys
import xml.etree.ElementTree as ET


def write_file(filename, content):
    '''
    Write file to args.output_dir
    Create directory if doesnt exist
    '''
    output_dir = args['output_dir']
    out_filepath = os.path.join(output_dir ,filename)
    if not os.path.exists(os.path.dirname(out_filepath)):
        try:
            os.makedirs(os.path.dirname(out_filepath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    logger.info("Writing new XML to file: %s"%out_filepath)
    with open(out_filepath, "w") as f:
        f.write(content)


def main(argv):

    xpath,new_value = args['xpath']
    files = args['files']

    for f in files:
        logger.info("Parsing: %s"%f.name)
        tree = ET.parse(f)
        root = tree.getroot()
        for xpath,new_value in args['xpath']:
            elems = root.findall(xpath)
            for elem in elems:
                logger.info("Replacing: %s. Old: %s, New: %s"%(xpath,elem.text, new_value))
                elem.text = new_value
        xmlstr = ET.tostring(root, encoding='utf8', method='xml')
        write_file(f.name, xmlstr)


if __name__ == "__main__":
    main(sys.argv)
    logger.info("Done!")
