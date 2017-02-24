# -*- coding: utf-8 -*-
import os

import sqlite3

from ..tags import TAGS_DELIMITER, decode_tag


class Hanchan(object):
    log_id = None
    is_tonpusen = False
    year = None
    content = None
    tags = None

    def __init__(self, log_id, is_tonpusen, year, content):
        self.log_id = log_id
        self.is_tonpusen = is_tonpusen,
        self.year = year,
        self.content = content

        self._decode_tags()

    def _decode_tags(self):
        self.tags = []
        temp = self.content.split(TAGS_DELIMITER)
        for item in temp:
            self.tags.append(decode_tag(item))


class ProcessDataCase(object):
    db_file = ''
    hanchans = []

    def __init__(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        self.db_file = os.path.join(current_directory, '..', 'data.db')

        self.hanchans = []

    def process(self):
        raise NotImplemented()

    def load_all_records(self):
        connection = sqlite3.connect(self.db_file)

        with connection:
            cursor = connection.cursor()

            cursor.execute('SELECT log_id, is_tonpusen, year, log FROM logs WHERE is_processed = 1 and was_error = 0;')
            data = cursor.fetchall()

        for item in data:
            self.hanchans.append(Hanchan(item[0], item[1] == 1, item[2], item[3]))
