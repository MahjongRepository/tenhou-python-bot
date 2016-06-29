# -*- coding: utf-8 -*-
import logging


def set_up_logging():
    logger = logging.getLogger('game')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(levelname)s %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)
