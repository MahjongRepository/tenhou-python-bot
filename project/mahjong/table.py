# -*- coding: utf-8 -*-
from mahjong.constants import EAST, SOUTH, WEST, NORTH
from mahjong.meld import Meld
from mahjong.player import Player
from mahjong.tile import Tile
from mahjong.utils import plus_dora, is_aka_dora


class Table(object):
    players = []

    dora_indicators = []

    dealer_seat = 0
    round_number = 0
    count_of_riichi_sticks = 0
    count_of_honba_sticks = 0

    count_of_remaining_tiles = 0
    count_of_players = 4

    # array of tiles in 34 format
    revealed_tiles = []

    def __init__(self, use_previous_ai_version=False):
        self.dora_indicators = []
        self._init_players(use_previous_ai_version)
        self.revealed_tiles = [0] * 34

    def __str__(self):
        return 'Round: {0}, Honba: {1}, Dora Indicators: {2}'.format(self.round_number,
                                                                     self.count_of_honba_sticks,
                                                                     self.dora_indicators)

    def init_round(self, round_number, count_of_honba_sticks, count_of_riichi_sticks,
                   dora_indicator, dealer_seat, scores):

        self.round_number = round_number
        self.count_of_honba_sticks = count_of_honba_sticks
        self.count_of_riichi_sticks = count_of_riichi_sticks

        self.dora_indicators = []
        self.add_dora_indicator(dora_indicator)

        self.revealed_tiles = [0] * 34

        # erase players state
        for player in self.players:
            player.erase_state()
            player.dealer_seat = dealer_seat

        self.set_players_scores(scores)

        # 136 - total count of tiles
        # 14 - tiles in dead wall
        # 13 - tiles in each player hand
        self.count_of_remaining_tiles = 136 - 14 - self.count_of_players * 13

    def init_main_player_hand(self, tiles):
        self.get_main_player().init_hand(tiles)

    def add_called_meld(self, player_seat, meld):
        # when opponent called meld it is means
        # that he discards tile from hand, not from wall
        self.count_of_remaining_tiles += 1

        self.get_player(player_seat).add_called_meld(meld)

        tiles = meld.tiles[:]
        # called tile was already added to revealed array
        # because of discard
        # for closed kan we will not have called_tile
        if meld.called_tile:
            tiles.remove(meld.called_tile)

        # for chankan we already added 3 tiles
        if meld.type == Meld.CHAKAN:
            tiles = tiles[0]

        for tile in tiles:
            self._add_revealed_tile(tile)

    def add_dora_indicator(self, tile):
        self.dora_indicators.append(tile)
        self._add_revealed_tile(tile)

    def is_dora(self, tile):
        return plus_dora(tile, self.dora_indicators) or is_aka_dora(tile)

    def set_players_scores(self, scores, uma=None):
        for i in range(0, len(scores)):
            self.get_player(i).scores = scores[i] * 100

            if uma:
                self.get_player(i).uma = uma[i]

        self.recalculate_players_position()

    def recalculate_players_position(self):
        temp_players = self.get_players_sorted_by_scores()
        for i in range(0, len(temp_players)):
            temp_player = temp_players[i]
            self.get_player(temp_player.seat).position = i + 1

    def set_players_names_and_ranks(self, values):
        for x in range(0, len(values)):
            self.get_player(x).name = values[x]['name']
            self.get_player(x).rank = values[x]['rank']

    def get_player(self, player_seat) -> Player:
        return self.players[player_seat]

    def get_main_player(self) -> Player:
        return self.players[0]

    def get_players_sorted_by_scores(self):
        return sorted(self.players, key=lambda x: x.scores, reverse=True)

    def enemy_discard(self, player_seat, tile, is_tsumogiri):
        """
        :param player_seat:
        :param tile: 136 format tile
        :param is_tsumogiri: was tile discarded from hand or not
        :return:
        """
        self.get_player(player_seat).add_discarded_tile(Tile(tile, is_tsumogiri))
        self.count_of_remaining_tiles -= 1

        for player in self.players:
            if player.in_riichi:
                player.safe_tiles.append(tile)

        # cache already revealed tiles
        self._add_revealed_tile(tile)

    def _init_players(self, use_previous_ai_version=False):
        self.players = []

        for seat in range(0, self.count_of_players):
            player = Player(seat=seat,
                            dealer_seat=0,
                            table=self,
                            use_previous_ai_version=use_previous_ai_version)
            self.players.append(player)

    @property
    def round_wind(self):
        if self.round_number < 4:
            return EAST
        elif 4 <= self.round_number < 8:
            return SOUTH
        elif 8 <= self.round_number < 12:
            return WEST
        else:
            return NORTH

    def _add_revealed_tile(self, tile):
        tile //= 4
        self.revealed_tiles[tile] += 1
