# -*- coding: utf-8 -*-
import bz2
import os
import sqlite3
import logging

import re

from tenhou.decoder import TenhouDecoder

logger = logging.getLogger('process')


class Game(object):
    year = None
    log_id = None
    is_tonpusen = False
    content = None
    rounds = []

    total_rounds = 0

    def __init__(self, log_id, is_tonpusen, compressed_content):
        self.log_id = log_id
        self.year = int(log_id[0:4])
        self.is_tonpusen = is_tonpusen
        self.content = str(bz2.decompress(compressed_content))
        self.rounds = []
        self.total_rounds = 0

        self._parse_rounds()

    def _parse_rounds(self):
        # we had to parse it manually, to save resources
        tag_start = 0
        tag = None
        game_round = []
        for x in range(0, len(self.content)):
            if self.content[x] == '>':
                tag = self.content[tag_start:x+1]
                tag_start = x + 1

            # not useful tags
            if tag and ('mjloggm' in tag or 'TAIKYOKU' in tag):
                tag = None

            # new round was started
            if tag and 'INIT' in tag:
                self.rounds.append(game_round)
                game_round = []
                self.total_rounds += 1

            # the end of the game
            if tag and 'owari' in tag:
                self.rounds.append(game_round)

            if tag:
                # to save some memory we can remove not needed information from logs
                if 'INIT' in tag:
                    # we dont need seed information
                    find = re.compile(r'shuffle="[^"]*"')
                    tag = find.sub('', tag)

                # add processed tag to the round
                game_round.append(tag)
                tag = None

        # first element is player names, ranks and etc.
        # we shouldn't consider it as game round
        # and for now let's not save it
        self.rounds = self.rounds[1:]


class ProcessDataCase(object):
    decoder = None
    db_file = None
    games = None

    def __init__(self, db_file):
        self.db_file = db_file
        self.decoder = TenhouDecoder()
        self.current_directory = os.path.dirname(os.path.realpath(__file__))

        self.games = []

    def process(self):
        raise NotImplemented()

    def load_all_records(self):
        # useful for debugging
        limit = None
        logger.info('Loading data...')

        connection = sqlite3.connect(self.db_file)

        with connection:
            cursor = connection.cursor()

            if limit:
                cursor.execute("""SELECT log_id, is_tonpusen, log_content FROM logs
                                  WHERE is_processed = 1 and was_error = 0 LIMIT ?;""", [limit])
            else:
                cursor.execute("""SELECT log_id, is_tonpusen, log_content FROM logs
                                  WHERE is_processed = 1 and was_error = 0;""")

            data = cursor.fetchall()

        logger.info('Found {} games records'.format(len(data)))

        logger.info('Unzipping and processing games data...')
        for item in data:
            self.games.append(Game(item[0], item[1] == 1, item[2]))

        total_rounds = 0
        for hanchan in self.games:
            total_rounds += hanchan.total_rounds

        logger.info('Found {} rounds'.format(total_rounds))
