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

    def add_called_meld(self, meld):
        # when opponent called meld it is means
        # that he discards tile from hand, not from wall
        self.table.count_of_remaining_tiles += 1

        return self.table.get_player(meld.who).add_called_meld(meld)

    def enemy_discard(self, tile, player_seat):
        """
        :param player_seat:
        :param tile: 136 format tile
        :return:
        """
        self.table.get_player(player_seat).add_discarded_tile(tile)
        self.table.count_of_remaining_tiles -= 1

        for player in self.table.players:
            if player.in_riichi:
                player.safe_tiles.append(tile)

    def enemy_riichi(self, player_seat):
        self.table.get_player(player_seat).in_riichi = True
