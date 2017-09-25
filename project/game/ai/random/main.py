# -*- coding: utf-8 -*-
import random

from game.ai.base.main import InterfaceAI


class ImplementationAI(InterfaceAI):
    """
    AI that will discard random tile from the hand
    """
    version = 'random'

    def discard_tile(self, discard_tile):
        tile_to_discard = random.randrange(len(self.player.tiles) - 1)
        tile_to_discard = self.player.tiles[tile_to_discard]
        return tile_to_discard
