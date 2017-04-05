# -*- coding: utf-8 -*-

import logging
import sqlite3

from analytics.cases.main import ProcessDataCase

logger = logging.getLogger('process')


class AnalyzeHonitsuHands(ProcessDataCase):
    HONITSU_ID = 34
    CHINITSU_ID = 35

    def process(self):
        self.calculate_statistics()
        logger.info('Done')

    def calculate_statistics(self):
        results = self._load_data()
        count_of_records = len(results)

        shanten_stat = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for result in results:
            shanten_stat[result['open_hand_shanten']] += 1

        for key in shanten_stat.keys():
            shanten_stat[key] = (shanten_stat[key] / count_of_records) * 100

        logger.info('Count of records: {}'.format(count_of_records))
        logger.info('Shanten stat: {}'.format(list(shanten_stat.values())))

    def _load_data(self):
        logger.info('Loading data...')

        results = []
        connection = sqlite3.connect(self.db_file)
        with connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * from data WHERE yaku = 34 and is_open_hand = 1;')
            data = cursor.fetchall()

            keys = ['is_honor_or_suit_dora', 'is_open_hand', 'is_tonpusen', 'is_tsumo',
                    'log_id', 'open_hand_shanten', 'open_hand_step',
                    'round_content', 'round_number', 'scores', 'suit',
                    'tempai_step', 'winner', 'winner_position', 'yaku', 'year']

            for result in data:
                dict_result = {}
                for key_index in range(0, len(keys)):
                    key = keys[key_index]
                    dict_result[key] = result[key_index]

                results.append(dict_result)

        return results
