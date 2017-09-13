# pylint: disable=line-too-long,C0103
from __future__ import print_function

'''
Generic functions that might be help to debug stuff inside mantid

'''
from mantid.simpleapi import logger

def print_properties(ws_name):
    ws = mtd[ws_name]
    run = ws.getRun()
    for key in run.keys():
        logger.notice("{:<40} {:>40}".format(key, run.getProperty(key).value))
