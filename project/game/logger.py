# -*- coding: utf-8 -*-
import logging

import datetime
import os


def set_up_logging():
    logs_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'logs')
    if not os.path.exists(logs_directory):
        os.mkdir(logs_directory)

    logger = logging.getLogger('game')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    file_name = datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S') + '.log'
    fh = logging.FileHandler(os.path.join(logs_directory, file_name))
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
