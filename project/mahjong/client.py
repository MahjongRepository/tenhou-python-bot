# -*- coding: utf-8 -*-
from mahjong.stat import Statistics
from mahjong.table import Table


class Client(object):
    statistics = None

    def __init__(self):
        self.table = Table()
        self.statistics = Statistics()
        self.player = self.table.get_main_player()

    def authenticate(self):
        pass

    def start_game(self):
        pass

    def end_game(self):
        pass

    def init_hand(self, tiles):
        self.player.init_hand(tiles)

    def draw_tile(self, tile):
        self.table.count_of_remaining_tiles -= 1
        self.player.draw_tile(tile)

    def discard_tile(self):
        return self.player.discard_tile()

    def call_meld(self, meld):
        # when opponent called meld it is means
        # that he will not get the tile from the wall
        # so, we need to compensate "-" from enemy discard method
        self.table.count_of_remaining_tiles += 1

        return self.table.get_player(meld.who).add_meld(meld)

    def enemy_discard(self, player_seat, tile):
        self.table.get_player(player_seat).add_discarded_tile(tile)
        self.table.count_of_remaining_tiles -= 1
