from mahjong.ai.base import BaseAI

from mahjong.tile import Tile


# Glossary:
# Shanten (向聴) - the number of tiles away from or one away from ready (tempai)

class FirstAI(BaseAI):
    player = None

    def __init__(self, player):
        super().__init__(player)

    def discard_tile(self):
        pass

    def calculate_outs(self):
        tiles = sorted(self.player.tiles)
        print(tiles)
        print (Tile.prepare_to_tenhou_analyzer(tiles))
        print([i.as_data() for i in tiles])
        return 0
