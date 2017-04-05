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
from analytics.cases.fold_against_honitsu_hands import AnalyzeHonitsuHands
ANALYTICS_CLASS = AnalyzeHonitsuHands

logger = logging.getLogger('process')


def main():
    set_up_logging()

    if len(sys.argv) == 1:
        logger.error('Cant find db file. Set db file location as command line argument')
        return

    db_file = sys.argv[1]
    if not os.path.exists(db_file):
        logger.error('Db file is not exists')

    db_name = os.path.split(db_file)[-1]
    logger.info(db_name)

    case = ANALYTICS_CLASS(db_file)
    case.process()


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
