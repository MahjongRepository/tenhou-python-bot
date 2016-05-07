import random

from mahjong.ai.random import RandomAI
from mahjong.tile import Tile


class Player(object):
    ai_class = RandomAI
    # the place where is player is sitting
    seat = 0
    # position based on scores
    position = 0
    scores = 0
    uma = 0

    name = ''
    rank = ''

    table = None
    discards = None
    tiles = None
    melds = None
    is_dealer = False

    def __init__(self, seat, table):
        self.discards = []
        self.melds = []
        self.tiles = []
        self.seat = seat
        self.table = table

        self.ai = self.ai_class(self)

    def __str__(self):
        result = u'{0}'.format(self.name)
        if self.scores:
            result += u' ({:,d})'.format(int(self.scores * 100))
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
        return self.ai.discard_tile()

    def erase_state(self):
        self.discards = []
        self.melds = []
        self.tiles = []
        self.is_dealer = False

        self.ai = self.ai_class(self)
