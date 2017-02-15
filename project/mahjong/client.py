# -*- coding: utf-8 -*-
from mahjong.stat import Statistics
from mahjong.table import Table
from utils.general import make_random_letters_and_digit_string


class Client(object):
    statistics = None
    id = ''
    seat = 0

    def __init__(self, use_previous_ai_version=False):
        self.table = Table(use_previous_ai_version)
        self.statistics = Statistics()
        self.player = self.table.get_main_player()
        self.id = make_random_letters_and_digit_string()

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

    def discard_tile(self, tile=None):
        return self.player.discard_tile(tile)

    def enemy_riichi(self, player_seat):
        self.table.get_player(player_seat).in_riichi = True
