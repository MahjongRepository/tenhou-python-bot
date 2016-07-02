# -*- coding: utf-8 -*-
import logging

from mahjong.ai.shanten import Shanten
from mahjong.tile import Tile

logger = logging.getLogger('tenhou')


class Player(object):
    # the place where is player is sitting
    seat = 0
    # position based on scores
    position = 0
    scores = 0
    uma = 0

    name = ''
    rank = ''

    discards = []
    # tiles that were discarded after player's riichi
    safe_tiles = []
    tiles = []
    melds = []
    table = None
    is_dealer = False
    in_tempai = False
    in_riichi = False
    in_defence_mode = False

    def __init__(self, seat, table, use_previous_ai_version=False):
        self.discards = []
        self.melds = []
        self.tiles = []
        self.safe_tiles = []
        self.seat = seat
        self.table = table

        if use_previous_ai_version:
            try:
                from mahjong.ai.old_version import MainAI
            # project wasn't set up properly
            # we don't have old version
            except ImportError:
                logger.error('Wasn\'t able to load old api version')
                from mahjong.ai.main import MainAI
        else:
            from mahjong.ai.main import MainAI

        self.ai = MainAI(table, self)

    def __str__(self):
        result = u'{0}'.format(self.name)
        if self.scores:
            result += u' ({:,d})'.format(int(self.scores))
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
        self.tiles = [Tile(i) for i in tiles]

    def draw_tile(self, tile):
        self.tiles.append(Tile(tile))
        # we need sort it to have a better string presentation
        self.tiles = sorted(self.tiles)

    def discard_tile(self):
        tile_to_discard = self.ai.discard_tile()
        if tile_to_discard != Shanten.AGARI_STATE:
            self.add_discarded_tile(tile_to_discard)
            self.tiles.remove(tile_to_discard)
        return tile_to_discard

    def erase_state(self):
        self.discards = []
        self.melds = []
        self.tiles = []
        self.safe_tiles = []
        self.is_dealer = False
        self.in_tempai = False
        self.in_riichi = False
        self.in_defence_mode = False

    def can_call_riichi(self):
        return all([
            self.in_tempai,
            not self.in_riichi,
            self.scores >= 1000,
            self.table.count_of_remaining_tiles > 4
        ])
