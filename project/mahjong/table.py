# -*- coding: utf-8 -*-
from mahjong.player import Player
from mahjong.utils import plus_dora, is_aka_dora


class Table(object):
    players = []

    dora_indicators = []

    round_number = 0
    count_of_riichi_sticks = 0
    count_of_honba_sticks = 0

    count_of_remaining_tiles = 0
    count_of_players = 4

    def __init__(self, use_previous_ai_version=False):
        self.dora_indicators = []
        self._init_players(use_previous_ai_version)

    def __str__(self):
        return 'Round: {0}, Honba: {1}, Dora Indicators: {2}'.format(self.round_number,
                                                                     self.count_of_honba_sticks,
                                                                     self.dora_indicators)

    def init_round(self, round_number, count_of_honba_sticks, count_of_riichi_sticks,
                   dora_indicator, dealer, scores):

        self.round_number = round_number
        self.count_of_honba_sticks = count_of_honba_sticks
        self.count_of_riichi_sticks = count_of_riichi_sticks

        self.dora_indicators = []
        self.add_dora_indicator(dora_indicator)

        # erase players state
        [i.erase_state() for i in self.players]

        self.get_player(dealer).is_dealer = True

        self.set_players_scores(scores)

        # 136 - total count of tiles
        # 14 - tiles in dead wall
        # 13 - tiles in each player hand
        self.count_of_remaining_tiles = 136 - 14 - self.count_of_players * 13

    def init_main_player_hand(self, tiles):
        self.get_main_player().init_hand(tiles)

    def add_open_set(self, meld):
        self.get_player(meld.who).add_meld(meld)

    def add_dora_indicator(self, tile):
        self.dora_indicators.append(tile)

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

    def _init_players(self, use_previous_ai_version=False):
        self.players = []

        for seat in range(0, self.count_of_players):
            player = Player(seat=seat, table=self, use_previous_ai_version=use_previous_ai_version)
            self.players.append(player)
