# -*- coding: utf-8 -*-
import re

import logging

from analytics.cases.main import ProcessDataCase

logger = logging.getLogger('process')


class HonitsuHands(ProcessDataCase):
    HONITSU_ID = '34'

    def process(self):
        self.load_all_records()

        filtered_rounds = self.filter_rounds()
        logger.info('Found {} honitsu hands'.format(len(filtered_rounds)))

    def filter_rounds(self):
        """
        Find all rounds that were ended with honitsu hand
        """
        filtered_rounds = []

        total_rounds = []
        for hanchan in self.hanchans:
            total_rounds.extend(hanchan.rounds)

        find = re.compile(r'yaku=\"(.+?)\"')
        for round_item in total_rounds:
            for tag in round_item:
                if 'AGARI' in tag and 'yaku=' in tag:
                    yaku_temp = find.findall(tag)[0].split(',')
                    # start at the beginning at take every second item (even)
                    yaku_list = yaku_temp[::2]

                    if self.HONITSU_ID in yaku_list:
                        filtered_rounds.append(round_item)

        return filtered_rounds
