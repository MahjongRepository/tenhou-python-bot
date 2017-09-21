# -*- coding: utf-8 -*-
from game.table import Table


class Client(object):
    table = None

    def __init__(self):
        self.table = Table()

    def connect(self):
        raise NotImplemented()

    def authenticate(self):
        raise NotImplemented()

    def start_game(self):
        raise NotImplemented()

    def end_game(self):
        raise NotImplemented()

    @property
    def player(self):
        return self.table.player
