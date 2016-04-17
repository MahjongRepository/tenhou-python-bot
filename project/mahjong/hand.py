import random

from mahjong.tile import Tile


class Player(object):
    number = 0
    discards = []
    open_sets = []
    is_dealer = False

    def __init__(self, number):
        self.discards = []
        self.open_sets = []
        self.number = number

    def __str__(self):
        return 'Open sets: {0} \nDiscards: {1}'.format(self.open_sets, self.discards)

    def add_open_set(self, meld):
        self.open_sets.append(meld)

    def add_discard(self, tile):
        self.discards.append(Tile(tile))


class PlayerHand(object):
    tiles = []

    def __init__(self):
        self.tiles = []

    def set_initial_hand(self, tiles):
        self.tiles = tiles

    def draw_tile(self, tile):
        self.tiles.append(tile)

    def discard_tile(self):
        # it will be complex logic for determination of discard tile (someday)
        # but for now it is just random discard
        tile_to_discard = random.randrange(len(self.tiles) - 1)
        tile_to_discard = self.tiles[tile_to_discard]

        self._remove_tile(tile_to_discard)

        return tile_to_discard

    def should_set_be_called(self, tile):
        return False

    def _remove_tile(self, tile):
        self.tiles.remove(tile)