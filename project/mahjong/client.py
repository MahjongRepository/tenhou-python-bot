# -*- coding: utf-8 -*-
from mahjong.stat import Statistics
from mahjong.table import Table


class Client(object):
    statistics = None

    def __init__(self):
        self.table = Table()
        self.statistics = Statistics()

    def authenticate(self):
        pass

    def start_game(self):
        pass

    def end_game(self):
        pass

    def draw_tile(self, tile):
        self.table.get_main_player().draw_tile(tile)

    def discard_tile(self):
        return self.table.get_main_player().discard_tile()

    def call_meld(self, meld):
        return self.table.get_player(meld.who).add_meld(meld)

    def enemy_discard(self, player_seat, tile):
        self.table.get_player(player_seat).add_discarded_tile(tile)
