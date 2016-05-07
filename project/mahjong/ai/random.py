import random

from mahjong.ai.base import BaseAI


# AI that will discard random tile from the hand
class RandomAI(BaseAI):

    def __init__(self, player):
        super().__init__(player)

    def discard_tile(self):
        tile_to_discard = random.randrange(len(self.player.tiles) - 1)
        tile_to_discard = self.player.tiles[tile_to_discard]

        self.player.tiles.remove(tile_to_discard)

        self.player.add_discarded_tile(tile_to_discard)

        return tile_to_discard
