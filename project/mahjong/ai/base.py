from mahjong.ai import random


class BaseAI(object):
    player = None

    def __init__(self, player):
        self.player = player

    def discard_tile(self):
        pass
