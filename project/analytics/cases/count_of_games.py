# -*- coding: utf-8 -*-
import sqlite3

import logging

from analytics.cases.main import ProcessDataCase

logger = logging.getLogger('process')


class CountOfGames(ProcessDataCase):

    def process(self):
        connection = sqlite3.connect(self.db_file)

        with connection:
            cursor = connection.cursor()

            total_games_sql = 'SELECT count(*) from logs'
            hanchan_games_sql = 'SELECT count(*) from logs where is_tonpusen = 0;'

            cursor.execute(total_games_sql)
            data = cursor.fetchone()
            total_games = data and data[0] or 0

            cursor.execute(hanchan_games_sql)
            data = cursor.fetchone()
            hanchan_games = data and data[0] or 0

            tonpusen_games = total_games - hanchan_games

            hanchan_percentage = total_games and (hanchan_games / total_games) * 100 or 0
            tonpusen_percentage = total_games and (tonpusen_games / total_games) * 100 or 0

            logger.info('Total games: {}'.format(total_games))
            logger.info('Hanchan games: {}, {:.2f}%'.format(hanchan_games, hanchan_percentage))
            logger.info('Tonpusen games: {}, {:.2f}%'.format(tonpusen_games, tonpusen_percentage))
            logger.info('')
