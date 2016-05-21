# -*- coding: utf-8 -*-
import random
from mahjong.ai.base import BaseAI


class RandomAI(BaseAI):
    """
    AI that will discard random tile from the hand
    """

    def __init__(self, player):
        super(RandomAI, self).__init__(player)

    def discard_tile(self):
        tile_to_discard = random.randrange(len(self.player.tiles) - 1)
        tile_to_discard = self.player.tiles[tile_to_discard]
        return tile_to_discard
