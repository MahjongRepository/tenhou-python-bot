# -*- coding: utf-8 -*-
from random import randint, shuffle, random

from mahjong.tile import TilesConverter

seed = random


class GameManager(object):
    """
    Draft of bots runner.
    Is not completed yet
    """

    tiles = []
    dead_wall = []
    players = []
    dora_indicators = []
    player_scores = []

    dealer = None
    current_player = None
    round_number = 0
    honba_sticks = 0
    riichi_sticks = 0


    def __init__(self, players):
        self.tiles = []
        self.dead_wall = []
        self.dora_indicators = []
        self.player_scores = []
        self.dealer = None
        self.players = players

    def init_round(self):
        self.tiles = [i for i in range(0, 136)]

        # need to change random function in future
        shuffle(self.tiles, seed)

        self.dead_wall = self._cut_tiles_from_array(14)
        self.dora_indicators.append(self.dead_wall[8])
        self.dealer = randint(0, 3)
        self.current_player = self.dealer
        self.player_scores = [25000 for _ in self.players]

        for player in self.players:
            player.table.init_round(
                self.round_number,
                self.honba_sticks,
                self.riichi_sticks,
                self.dora_indicators[0],
                self.dealer,
                self.player_scores
            )
            player.init_hand(self._cut_tiles_from_array(13))

    def play_round(self):

        while len(self.tiles):
            for player in self.players:
                if len(player.tiles) == 14:
                    print(TilesConverter.to_one_line_string(player.tiles))

            self.draw_tile()
            self.discard_tile()

        self.round_number += 1

    def draw_tile(self):
        tile = self._cut_tiles_from_array(1)[0]
        self.get_player(self.current_player).draw_tile(tile)

    def discard_tile(self):
        self.get_player(self.current_player).discard_tile()

        self.current_player += 1
        if self.current_player > 3:
            self.current_player = 0

    def get_player(self, player_seat):
        return self.players[player_seat]

    def _cut_tiles_from_array(self, count_of_tiles):
        result = self.tiles[0:count_of_tiles]
        self.tiles = self.tiles[count_of_tiles:len(self.tiles)]
        return result

