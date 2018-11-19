# -*- coding: utf-8 -*-
from mahjong.constants import EAST, SOUTH, WEST, NORTH
from mahjong.meld import Meld
from mahjong.tile import TilesConverter, Tile
from mahjong.utils import plus_dora, is_aka_dora

from game.player import Player, EnemyPlayer


class Table(object):
    # our bot
    player = None
    # main bot + all other players
    players = None

    dora_indicators = None

    dealer_seat = 0
    round_number = -1
    round_wind_number = 0
    count_of_riichi_sticks = 0
    count_of_honba_sticks = 0

    count_of_remaining_tiles = 0
    count_of_players = 4

    meld_was_called = False

    # array of tiles in 34 format
    revealed_tiles = None

    has_open_tanyao = False
    has_aka_dora = False

    def __init__(self):
        self._init_players()
        self.dora_indicators = []
        self.revealed_tiles = [0] * 34

    def __str__(self):
        dora_string = TilesConverter.to_one_line_string(self.dora_indicators)

        round_settings = {
            EAST:  ['e', 0],
            SOUTH: ['s', 3],
            WEST:  ['w', 7]
        }.get(self.round_wind_tile)

        round_string, round_diff = round_settings
        display_round = '{}{}'.format(round_string, (self.round_wind_number + 1) - round_diff)

        return 'Round: {}, Honba: {}, Dora Indicators: {}'.format(
            display_round,
            self.count_of_honba_sticks,
            dora_string
        )

    def init_round(self,
                   round_wind_number,
                   count_of_honba_sticks,
                   count_of_riichi_sticks,
                   dora_indicator,
                   dealer_seat,
                   scores):

        # we need it to properly display log for each round
        self.round_number += 1

        self.meld_was_called = False
        self.dealer_seat = dealer_seat
        self.round_wind_number = round_wind_number
        self.count_of_honba_sticks = count_of_honba_sticks
        self.count_of_riichi_sticks = count_of_riichi_sticks

        self.revealed_tiles = [0] * 34

        self.dora_indicators = []
        self.add_dora_indicator(dora_indicator)

        # erase players state
        for player in self.players:
            player.erase_state()
            player.dealer_seat = dealer_seat
        self.set_players_scores(scores)

        # 136 - total count of tiles
        # 14 - tiles in dead wall
        # 13 - tiles in each player hand
        self.count_of_remaining_tiles = 136 - 14 - self.count_of_players * 13

        if round_wind_number == 0 and count_of_honba_sticks == 0:
            i = 0
            seats = [0, 1, 2, 3]
            for player in self.players:
                player.first_seat = seats[i - dealer_seat]
                i += 1

    def add_called_meld(self, player_seat, meld):
        self.meld_was_called = True

        # when opponent called meld it is means
        # that he discards tile from hand, not from wall
        self.count_of_remaining_tiles += 1

        # we will decrease count of remaining tiles after called kan
        # because we had to complement dead wall
        if meld.type == Meld.KAN or meld.type == meld.CHANKAN:
            self.count_of_remaining_tiles -= 1

        self.get_player(player_seat).add_called_meld(meld)

        tiles = meld.tiles[:]
        # called tile was already added to revealed array
        # because it was called on the discard
        if meld.called_tile is not None:
            tiles.remove(meld.called_tile)

        # for chankan we already added 3 tiles
        if meld.type == meld.CHANKAN:
            tiles = [meld.tiles[0]]

        for tile in tiles:
            self._add_revealed_tile(tile)

    def add_called_riichi(self, player_seat):
        self.get_player(player_seat).in_riichi = True

        # we had to check will we go for defence or not
        if player_seat != 0:
            self.player.enemy_called_riichi(player_seat)

    def add_discarded_tile(self, player_seat, tile_136, is_tsumogiri):
        """
        :param player_seat:
        :param tile_136: 136 format tile
        :param is_tsumogiri: was tile discarded from hand or not
        """
        self.count_of_remaining_tiles -= 1

        tile = Tile(tile_136, is_tsumogiri)
        self.get_player(player_seat).add_discarded_tile(tile)

        # cache already revealed tiles
        self._add_revealed_tile(tile.value)

    def add_dora_indicator(self, tile):
        self.dora_indicators.append(tile)
        self._add_revealed_tile(tile)

    def is_dora(self, tile):
        return plus_dora(tile, self.dora_indicators) or is_aka_dora(tile, self.has_open_tanyao)

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

    def get_player(self, player_seat):
        return self.players[player_seat]

    def get_players_sorted_by_scores(self):
        return sorted(self.players, key=lambda x: (x.scores or 0, -x.first_seat), reverse=True)

    @property
    def round_wind_tile(self):
        if self.round_wind_number < 4:
            return EAST
        elif 4 <= self.round_wind_number < 8:
            return SOUTH
        elif 8 <= self.round_wind_number < 12:
            return WEST
        else:
            return NORTH

    def _add_revealed_tile(self, tile):
        tile //= 4
        self.revealed_tiles[tile] += 1

    def _init_players(self,):
        self.player = Player(self, 0, self.dealer_seat)

        self.players = [self.player]
        for seat in range(1, self.count_of_players):
            player = EnemyPlayer(self, seat, self.dealer_seat)
            self.players.append(player)
