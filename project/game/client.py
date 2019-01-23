# -*- coding: utf-8 -*-
from game.table import Table


class Client(object):
    table = None

    def __init__(self):
        self.table = Table()

    def connect(self):
        raise NotImplementedError()

    def authenticate(self):
        raise NotImplementedError()

    def start_game(self):
        raise NotImplementedError()

    def end_game(self):
        raise NotImplementedError()

    @property
    def player(self):
        return self.table.player
