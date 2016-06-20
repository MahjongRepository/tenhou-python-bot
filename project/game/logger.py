# -*- coding: utf-8 -*-
import logging


def set_up_logging():
    """
    Logger for game manager, so only for our tests
    """
    logger = logging.getLogger('game')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(levelname)s %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)
