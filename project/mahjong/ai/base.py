# -*- coding: utf-8 -*-


class BaseAI(object):
    player = None
    table = None

    def __init__(self, table, player):
        self.player = player
        self.table = table

    def discard_tile(self):
        pass
