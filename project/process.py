# -*- coding: utf-8 -*-
"""
Calculate various statistics on phoenix replays
"""
import os
import sys

import logging

import datetime

# from analytics.cases.count_of_games import CountOfGames
# ANALYTICS_CLASS = CountOfGames
from analytics.cases.honitsu_hands import HonitsuHands
ANALYTICS_CLASS = HonitsuHands

logger = logging.getLogger('process')


def main():
    set_up_logging()

    if len(sys.argv) == 1:
        logger.error('Cant find db files. Set db files folder as command line argument')
        return

    db_folder = sys.argv[1]
    for db_file in os.listdir(db_folder):
        logger.info(db_file)
        case = ANALYTICS_CLASS(os.path.join(db_folder, db_file))
        case.process()
        break


def set_up_logging():
    logs_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
    if not os.path.exists(logs_directory):
        os.mkdir(logs_directory)

    logger = logging.getLogger('process')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    file_name = datetime.datetime.now().strftime('process-%Y-%m-%d %H_%M_%S') + '.log'
    fh = logging.FileHandler(os.path.join(logs_directory, file_name))
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

if __name__ == '__main__':
    main()
