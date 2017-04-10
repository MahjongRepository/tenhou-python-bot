# -*- coding: utf-8 -*-
import logging
from functools import reduce

import copy

from mahjong.ai.defence.enemy_analyzer import EnemyAnalyzer
from mahjong.constants import EAST, SOUTH, WEST, NORTH
from mahjong.meld import Meld
from mahjong.tile import TilesConverter, Tile
from utils.settings_handler import settings

logger = logging.getLogger('tenhou')


class PlayerInterface(object):
    table = None
    discards = None
    melds = None
    in_riichi = None
    seat = 0
    # where is sitting dealer, based on this information we can calculate player wind
    dealer_seat = 0
    # position based on scores
    position = 0
    scores = 0
    uma = 0

    name = ''
    rank = ''

    previous_ai = False

    def __init__(self, table, seat, dealer_seat, previous_ai):
        self.table = table
        self.seat = seat
        self.dealer_seat = dealer_seat
        self.previous_ai = previous_ai

        self.erase_state()

    def __str__(self):
        result = u'{0}'.format(self.name)
        if self.scores:
            result += u' ({:,d})'.format(int(self.scores))
            if self.uma:
                result += u' {0}'.format(self.uma)
        else:
            result += u' ({0})'.format(self.rank)
        return result

    def __repr__(self):
        return self.__str__()

    def erase_state(self):
        self.discards = []
        self.melds = []
        self.in_riichi = False
        self.position = 0
        self.scores = 0
        self.uma = 0

    def add_called_meld(self, meld: Meld):
        self.melds.append(meld)

    def add_discarded_tile(self, tile: Tile):
        self.discards.append(tile)

        # all tiles that were discarded after player riichi will be safe against him
        # because of furiten
        tile = tile.value // 4
        for player in self.table.enemy_players:
            if player.in_riichi and tile not in player.safe_tiles:
                player.safe_tiles.append(tile)

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
    def meld_tiles(self):
        """
        Array of 136 tiles format
        :return:
        """
        meld_tiles = [x.tiles for x in self.melds]
        if meld_tiles:
            meld_tiles = reduce(lambda z, y: z + y, [x.tiles for x in self.melds])
        return meld_tiles


class Player(PlayerInterface):
    ai = None
    tiles = None
    last_draw = None
    in_tempai = False
    in_defence_mode = False

    def __init__(self, table, seat, dealer_seat, previous_ai):
        super().__init__(table, seat, dealer_seat, previous_ai)
        self._load_ai()

    def erase_state(self):
        super().erase_state()

        self.tiles = []
        self.last_draw = None
        self.in_tempai = False
        self.in_defence_mode = False

        if self.ai:
            self.ai.erase_state()

    def init_hand(self, tiles):
        self.tiles = tiles

        self.ai.determine_strategy()

    def draw_tile(self, tile):
        self.last_draw = tile
        self.tiles.append(tile)

        # we need sort it to have a better string presentation
        self.tiles = sorted(self.tiles)

        self.ai.determine_strategy()

    def discard_tile(self, discard_option=None):
        """
        :param discard_option:
        :return:
        """
        # we can't use if tile, because of 0 tile
        if discard_option:
            tile_to_discard = self.ai.process_discard_option(discard_option, self.closed_hand)
        else:
            tile_to_discard = self.ai.discard_tile()

        is_tsumogiri = tile_to_discard == self.last_draw
        # it is important to use table method,
        # to recalculate revealed tiles and etc.
        self.table.add_discarded_tile(0, tile_to_discard, is_tsumogiri)
        self.tiles.remove(tile_to_discard)

        return tile_to_discard

    def can_call_riichi(self):
        result = all([
            self.in_tempai,

            not self.in_riichi,
            not self.is_open_hand,

            self.scores >= 1000,
            self.table.count_of_remaining_tiles > 4
        ])

        return result and self.ai.should_call_riichi()

    def try_to_call_meld(self, tile, is_kamicha_discard):
        return self.ai.try_to_call_meld(tile, is_kamicha_discard)

    def total_tiles(self, tile, tiles_34):
        """
        Return sum of all tiles (discarded + from melds + our hand)
        :param tile: 34 tile format
        :param tiles_34: cached list of tiles (to not build it for each iteration)
        :return: int
        """
        return tiles_34[tile] + self.table.revealed_tiles[tile]

    def enemy_called_riichi(self):
        """
        After enemy riichi we had to check will we fold or not
        it is affect open hand decision
        :return:
        """
        if self.ai.defence.should_go_to_defence_mode():
            self.ai.in_defence = True

    def format_hand_for_print(self, tile):
        hand_string = '{} + {}'.format(
            TilesConverter.to_one_line_string(self.closed_hand),
            TilesConverter.to_one_line_string([tile])
        )
        if self.is_open_hand:
            melds = []
            for item in self.melds:
                melds.append('{}'.format(TilesConverter.to_one_line_string(item.tiles)))
            hand_string += ' [{}]'.format(', '.join(melds))
        return hand_string

    @property
    def closed_hand(self):
        tiles = self.tiles[:]
        return [item for item in tiles if item not in self.meld_tiles]

    @property
    def open_hand_34_tiles(self):
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

    def _load_ai(self):
        if self.previous_ai:
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

        self.ai = MainAI(self)


class EnemyPlayer(PlayerInterface):
    # array of tiles in 34 tile format
    safe_tiles = None
    # tiles that were discarded in the current "step"
    # so, for example kamicha discard will be a safe tile for all players
    temporary_safe_tiles = None
    enemy_analyzer = None

    def erase_state(self):
        super().erase_state()

        self.safe_tiles = []
        self.temporary_safe_tiles = []
        self.enemy_analyzer = EnemyAnalyzer(self)

    def add_discarded_tile(self, tile: Tile):
        super().add_discarded_tile(tile)

        tile = tile.value // 4
        if tile not in self.safe_tiles:
            self.safe_tiles.append(tile)

        # erase temporary furiten after tile draw
        self.temporary_safe_tiles = []
        affected_players = [1, 2, 3]
        affected_players.remove(self.seat)
        # temporary furiten, for one "step"
        for x in affected_players:
            if tile not in self.table.get_player(x).temporary_safe_tiles:
                self.table.get_player(x).temporary_safe_tiles.append(tile)

    @property
    def all_safe_tiles(self):
        return list(set(self.temporary_safe_tiles + self.safe_tiles))

    @property
    def in_tempai(self):
        """
        Try to detect is user in tempai or not
        :return: boolean
        """
        return self.enemy_analyzer.in_tempai

    @property
    def is_threatening(self):
        """
        Should we fold against this player or not
        :return: boolean
        """
        return self.enemy_analyzer.is_threatening

    @property
    def chosen_suit(self):
        """
        If user collecting honitsu we can detect his specific suit
        :return: function
        """
        return self.enemy_analyzer.chosen_suit
