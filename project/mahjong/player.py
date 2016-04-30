import random

from mahjong.tile import Tile


class Player(object):
    # the place where is player is sitting
    seat = 0
    # position based on scores
    position = 0
    scores = 0
    uma = 0
    name = ''
    rank = ''
    discards = None
    melds = None
    is_dealer = False

    def __init__(self, seat):
        self.discards = []
        self.melds = []
        self.tiles = []
        self.seat = seat

    def __str__(self):
        result = u'{0}'.format(self.name)
        if self.scores:
            result += u' ({0})'.format(self.scores)
            if self.uma:
                result += u' {0}'.format(self.uma)
        else:
            result += u' ({0})'.format(self.rank)
        return result

    # for calls in array
    def __repr__(self):
        return self.__str__()

    def add_meld(self, meld):
        self.melds.append(meld)

    def add_discarded_tile(self, tile):
        self.discards.append(Tile(tile))

    def init_hand(self, tiles):
        self.tiles = tiles

    def draw_tile(self, tile):
        self.tiles.append(tile)

    def discard_tile(self):
        # it will be complex logic for determination of discard tile (someday)
        # but for now it is just random discard
        tile_to_discard = random.randrange(len(self.tiles) - 1)
        tile_to_discard = self.tiles[tile_to_discard]

        self.tiles.remove(tile_to_discard)

        self.add_discarded_tile(tile_to_discard)

        return tile_to_discard
