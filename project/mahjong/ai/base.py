# -*- coding: utf-8 -*-


class BaseAI(object):
    player = None
    table = None

    def __init__(self, player):
        self.player = player

    def discard_tile(self):
        pass
