# -*- coding: utf-8 -*-
from mahjong.constants import AKA_DORA_LIST
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor, simplify, plus_dora, is_aka_dora


class DiscardOption(object):
    player = None

    # in 34 tile format
    tile_to_discard = None
    # array of tiles that will improve our hand
    waiting = None
    # how much tiles will improve our hand
    tiles_count = None
    # number of shanten for that tile
    shanten = None
    # sometimes we had to force tile to be discarded
    had_to_be_discarded = False
    # special cases where we had to save tile in hand (usually for atodzuke opened hand)
    had_to_be_saved = False
    # calculated tile value, for sorting
    valuation = None
    # how danger this tile is
    danger = None

    def __init__(self, player, tile_to_discard, shanten, waiting, tiles_count, danger=100):
        """
        :param player:
        :param tile_to_discard: tile in 34 format
        :param waiting: list of tiles in 34 format
        :param tiles_count: count of tiles to wait after discard
        """
        self.player = player
        self.tile_to_discard = tile_to_discard
        self.shanten = shanten
        self.waiting = waiting
        self.tiles_count = tiles_count
        self.danger = danger
        self.had_to_be_saved = False
        self.had_to_be_discarded = False

        self.calculate_value()

    def find_tile_in_hand(self, closed_hand):
        """
        Find and return 136 tile in closed player hand
        """

        if self.player.table.has_aka_dora:
            tiles_five_of_suits = [4, 13, 22]
            # special case, to keep aka dora in hand
            if self.tile_to_discard in tiles_five_of_suits:
                aka_closed_hand = closed_hand[:]
                while True:
                    tile = TilesConverter.find_34_tile_in_136_array(self.tile_to_discard, aka_closed_hand)

                    # we have only aka dora in the hand, without simple five
                    if not tile:
                        break

                    # we found aka in the hand,
                    # let's try to search another five tile
                    # to keep aka dora
                    if tile in AKA_DORA_LIST:
                        aka_closed_hand.remove(tile)
                    else:
                        return tile

        return TilesConverter.find_34_tile_in_136_array(self.tile_to_discard, closed_hand)

    def calculate_value(self, shanten=None):
        # base is 100 for ability to mark tiles as not needed (like set value to 50)
        value = 100
        honored_value = 20

        # we don't need to keep honor tiles in almost completed hand
        if shanten and shanten <= 2:
            honored_value = 0

        if is_honor(self.tile_to_discard):
            if self.tile_to_discard in self.player.valued_honors:
                count_of_winds = [x for x in self.player.valued_honors if x == self.tile_to_discard]
                # for west-west, east-east we had to double tile value
                value += honored_value * len(count_of_winds)
        else:
            # suits
            suit_tile_grades = [10, 20, 30, 40, 50, 40, 30, 20, 10]
            simplified_tile = simplify(self.tile_to_discard)
            value += suit_tile_grades[simplified_tile]

        count_of_dora = plus_dora(self.tile_to_discard * 4, self.player.table.dora_indicators)
        if is_aka_dora(self.tile_to_discard * 4, self.player.table.has_open_tanyao):
            count_of_dora += 1

        value += 50 * count_of_dora

        if is_honor(self.tile_to_discard):
            # depends on how much honor tiles were discarded
            # we will decrease tile value
            discard_percentage = [100, 75, 20, 0, 0]
            discarded_tiles = self.player.table.revealed_tiles[self.tile_to_discard]

            value = (value * discard_percentage[discarded_tiles]) / 100

            # three honor tiles were discarded,
            # so we don't need this tile anymore
            if value == 0:
                self.had_to_be_discarded = True

        self.valuation = value
