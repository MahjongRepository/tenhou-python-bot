# -*- coding: utf-8 -*-
from mahjong.stat import Statistics
from mahjong.table import Table
from utils.general import make_random_letters_and_digit_string


class Client(object):
    table = None
    player = None

    def __init__(self, use_previous_ai_version=False):
        self.table = Table(use_previous_ai_version)
        self.player = self.table.get_main_player()

    def connect(self):
        raise NotImplemented()

    def authenticate(self):
        raise NotImplemented()

    def start_game(self):
        raise NotImplemented()

    def end_game(self):
        raise NotImplemented()
