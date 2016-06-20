# -*- coding: utf-8 -*-

import datetime
import logging

import os


def set_up_logging():
    """
    Main logger for usual bot needs
    """
    logger = logging.getLogger('tenhou')
    logger.setLevel(logging.DEBUG)

    logs_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'logs')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    if not os.path.exists(logs_directory):
        os.mkdir(logs_directory)

    file_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.log'
    fh = logging.FileHandler(os.path.join(logs_directory, file_name))
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
