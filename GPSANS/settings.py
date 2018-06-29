'''
Created on Oct 29, 2015
@author: rhf
'''

import os
import logging
import logging.config
import ConfigParser as configparser
import argparse

CONFIG_FILE = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), 'config.cfg')
LOCAL_CONFIG_FILE = os.path.expanduser('~/.superimpose.cfg')


def get_parse_args():
    '''
    parse command line input arguments
    '''
    parser = argparse.ArgumentParser(
        description='Replaces XML values in files')
    parser.add_argument('files', metavar='file', type=argparse.FileType(
        'r'), nargs='+', help='files to parse')
    parser.add_argument('-o', '--output-dir', action='store_true', help='Where the files are beeing stored. Default: %s'%config.get('General', 'output_dir'),
                        required=False, default=config.get('General', 'output_dir'))
    parser.add_argument('-x', '--xpath', action='append', nargs=2, metavar=('XPATH', 'NEW_VALUE'),
                        help='XML Xpath followed by the value to assign to the selection. \
                        Only supports tag text replacement, not attributes, i.e.: <tag>text</tag>', required=True)
    args = vars(parser.parse_args())
    return args


def get_config():
    '''
    Parse .cfg file
    '''
    config = configparser.ConfigParser()
    # config.optionxform=str # case insensitive
    config.read([CONFIG_FILE, LOCAL_CONFIG_FILE])
    return config


def get_logger():
    logging.config.fileConfig(CONFIG_FILE, disable_existing_loggers=False)
    logger = logging.getLogger()
    return logger


config = get_config()
logger = get_logger()
args = get_parse_args()
