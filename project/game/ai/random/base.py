# -*- coding: utf-8 -*-
import random

from game.ai.base.base import BaseAI


class MainAI(BaseAI):
    """
    AI that will discard random tile from the hand
    """

    version = 'random'

    def __init__(self, player):
        super(MainAI, self).__init__(player)

    def discard_tile(self):
        tile_to_discard = random.randrange(len(self.player.tiles) - 1)
        tile_to_discard = self.player.tiles[tile_to_discard]
        return tile_to_discard
