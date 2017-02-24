# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime
from analytics.cases.main import ProcessDataCase


class CountOfGames(ProcessDataCase):

    def process(self):
        years = range(2009, datetime.now().year + 1)

        connection = sqlite3.connect(self.db_file)

        with connection:
            cursor = connection.cursor()

            tonpusen_games_array = []
            hanchan_games_array = []

            for year in years:
                total_games_sql = 'SELECT count(*) from logs where year = {};'.format(year)
                hanchan_games_sql = 'SELECT count(*) from logs where year = {} and is_tonpusen = 0;'.format(year)
                tonpusen_games_sql = 'SELECT count(*) from logs where year = {} and is_tonpusen = 1;'.format(year)

                cursor.execute(total_games_sql)
                data = cursor.fetchone()
                total_games = data and data[0] or 0

                cursor.execute(hanchan_games_sql)
                data = cursor.fetchone()
                hanchan_games = data and data[0] or 0

                cursor.execute(tonpusen_games_sql)
                data = cursor.fetchone()
                tonpusen_games = data and data[0] or 0

                hanchan_percentage = total_games and (hanchan_games / total_games) * 100 or 0
                tonpusen_percentage = total_games and (tonpusen_games / total_games) * 100 or 0

                print(year)
                print('Total games: {}'.format(total_games))
                print('Hanchan games: {}, {:.2f}%'.format(hanchan_games, hanchan_percentage))
                print('Tonpusen games: {}, {:.2f}%'.format(tonpusen_games, tonpusen_percentage))
                print()

                tonpusen_games_array.append(tonpusen_percentage)
                hanchan_games_array.append(hanchan_percentage)
