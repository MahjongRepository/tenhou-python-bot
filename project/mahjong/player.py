# -*- coding: utf-8 -*-
import logging
from functools import reduce

import copy

from mahjong.constants import EAST, SOUTH, WEST, NORTH
from utils.settings_handler import settings
from mahjong.ai.shanten import Shanten

logger = logging.getLogger('tenhou')


class Player(object):
    # the place where is player is sitting
    # always = 0 for our player
    seat = 0
    # where is sitting dealer, based on this information we can calculate player wind
    dealer_seat = 0
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
    last_draw = None
    in_tempai = False
    in_riichi = False
    in_defence_mode = False

    # system fields
    # for local games emulation
    _is_daburi = False
    _is_ippatsu = False

    def __init__(self, seat, dealer_seat, table, use_previous_ai_version=False):
        self.discards = []
        self.melds = []
        self.tiles = []
        self.safe_tiles = []
        self.seat = seat
        self.table = table
        self.dealer_seat = dealer_seat

        if use_previous_ai_version:
            try:
                from mahjong.ai.old_version import MainAI
            # project wasn't set up properly
            # we don't have old version
            except ImportError:
                logger.error('Wasn\'t able to load old api version')
                from mahjong.ai.main import MainAI
        else:
            if settings.ENABLE_AI:
                from mahjong.ai.main import MainAI
            else:
                from mahjong.ai.random import MainAI

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

    def erase_state(self):
        self.discards = []
        self.melds = []
        self.tiles = []
        self.safe_tiles = []

        self.last_draw = None
        self.in_tempai = False
        self.in_riichi = False
        self.in_defence_mode = False

        self.dealer_seat = 0

        self.ai.erase_state()

    def add_called_meld(self, meld):
        self.melds.append(meld)

    def add_discarded_tile(self, tile):
        self.discards.append(tile)

    def init_hand(self, tiles):
        self.tiles = tiles

        self.ai.determine_strategy()

    def draw_tile(self, tile):
        self.last_draw = tile
        self.tiles.append(tile)
        # we need sort it to have a better string presentation
        self.tiles = sorted(self.tiles)

        self.ai.determine_strategy()

    def discard_tile(self, tile=None):
        """
        We can say what tile to discard
        input tile = None we will discard tile based on AI logic
        :param tile: 136 tiles format
        :return:
        """
        tile_to_discard = tile or self.ai.discard_tile()

        if tile_to_discard != Shanten.AGARI_STATE:
            self.add_discarded_tile(tile_to_discard)
            self.tiles.remove(tile_to_discard)

        return tile_to_discard

    def can_call_riichi(self):
        return all([
            self.in_tempai,

            not self.in_riichi,
            not self.is_open_hand,

            self.scores >= 1000,
            self.table.count_of_remaining_tiles > 4
        ])

    def try_to_call_meld(self, tile, is_kamicha_discard):
        return self.ai.try_to_call_meld(tile, is_kamicha_discard)

    @property
    def player_wind(self):
        position = self.dealer_seat
        if position == 0:
            return EAST
        elif position == 1:
            return NORTH
        elif position == 2:
            return WEST
        else:
            return SOUTH

    @property
    def is_dealer(self):
        return self.seat == self.dealer_seat

    @property
    def is_open_hand(self):
        return len(self.melds) > 0

    @property
    def closed_hand(self):
        tiles = self.tiles[:]
        meld_tiles = [x.tiles for x in self.melds]
        if meld_tiles:
            meld_tiles = reduce(lambda z, y: z + y, [x.tiles for x in self.melds])
        return [item for item in tiles if item not in meld_tiles]

    @property
    def meld_tiles(self):
        """
        Array of array with 34 tiles indices
        :return: array
        """
        melds = [x.tiles for x in self.melds]
        melds = copy.deepcopy(melds)
        for meld in melds:
            meld[0] //= 4
            meld[1] //= 4
            meld[2] //= 4
        return melds
