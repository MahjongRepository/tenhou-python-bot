# -*- coding: utf-8 -*-
from mahjong.tile import TilesConverter


class DiscardOption(object):
    player = None

    # in 34 tile format
    tile_to_discard = None
    # array of tiles that will improve our hand
    waiting = None
    # how much tiles will improve our hand
    tiles_count = None

    def __init__(self, player, tile_to_discard, waiting, tiles_count):
        """
        :param player:
        :param tile_to_discard: tile in 34 format
        :param waiting: list of tiles in 34 format
        :param tiles_count: count of tiles to wait after discard
        """
        self.player = player
        self.tile_to_discard = tile_to_discard
        self.waiting = waiting
        self.tiles_count = tiles_count

    def find_tile_in_hand(self, closed_hand):
        """
        Find and return 136 tile in closed player hand
        """
        return TilesConverter.find_34_tile_in_136_array(self.tile_to_discard, closed_hand)
