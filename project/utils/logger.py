# -*- coding: utf-8 -*-

import datetime
import logging
import os
import hashlib

from utils.settings_handler import settings


def set_up_logging():
    """
    Logger for tenhou communication and AI output
    """
    logs_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'logs')
    if not os.path.exists(logs_directory):
        os.mkdir(logs_directory)

    # we shouldn't be afraid about collision
    # also, we need it to distinguish different bots logs (if they were run in the same time)
    name_hash = hashlib.sha1(settings.USER_ID.encode('utf-8')).hexdigest()[:5]

    logger = logging.getLogger('tenhou')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    file_name = '{}_{}.log'.format(name_hash, datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S'))
    fh = logging.FileHandler(os.path.join(logs_directory, file_name))
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    logger = logging.getLogger('ai')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.addHandler(fh)
