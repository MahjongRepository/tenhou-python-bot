# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.discard import DiscardOption
from mahjong.ai.shanten import Shanten
from mahjong.constants import EAST, SOUTH, WEST, NORTH, HAKU, HATSU, CHUN, FIVE_RED_SOU
from mahjong.player import Player
from mahjong.table import Table
from utils.tests import TestMixin
from utils.settings_handler import settings


class DiscardLogicTestCase(unittest.TestCase, TestMixin):

    def test_discard_tile(self):
        table = Table()
        player = Player(table, 0, 0, False)

        tiles = self._string_to_136_array(sou='11134567', pin='159', man='45')
        tile = self._string_to_136_tile(man='9')
        player.init_hand(tiles)
        player.draw_tile(tile)

        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '9m')

        player.draw_tile(self._string_to_136_tile(pin='4'))
        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '1p')

        player.draw_tile(self._string_to_136_tile(pin='3'))
        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '9p')

        player.draw_tile(self._string_to_136_tile(man='4'))
        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '5m')

        player.draw_tile(self._string_to_136_tile(sou='8'))
        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, Shanten.AGARI_STATE)

    def test_calculate_suit_tiles_value(self):
        settings.FIVE_REDS = False

        table = Table()
        player = Player(table, 0, 0, False)

        # 0 - 8   man
        # 9 - 17  pin
        # 18 - 26 sou
        results = [
            [0, 110], [9,  110], [18, 110],
            [1, 120], [10, 120], [19, 120],
            [2, 130], [11, 130], [20, 130],
            [3, 140], [12, 140], [21, 140],
            [4, 150], [13, 150], [22, 150],
            [5, 140], [14, 140], [23, 140],
            [6, 130], [15, 130], [24, 130],
            [7, 120], [16, 120], [25, 120],
            [8, 110], [17, 110], [26, 110]
        ]

        for item in results:
            tile = item[0]
            value = item[1]
            option = DiscardOption(player, tile, 0, [], 0)
            self.assertEqual(option.value, value)

        settings.FIVE_REDS = True

    def test_calculate_honor_tiles_value(self):
        table = Table()
        player = Player(table, 0, 0, False)
        player.dealer_seat = 3

        # valuable honor, wind of the round
        option = DiscardOption(player, EAST, 0, [], 0)
        self.assertEqual(option.value, 120)

        # valuable honor, wind of the player
        option = DiscardOption(player, SOUTH, 0, [], 0)
        self.assertEqual(option.value, 120)

        # not valuable wind
        option = DiscardOption(player, WEST, 0, [], 0)
        self.assertEqual(option.value, 100)

        # not valuable wind
        option = DiscardOption(player, NORTH, 0, [], 0)
        self.assertEqual(option.value, 100)

        # valuable dragon
        option = DiscardOption(player, HAKU, 0, [], 0)
        self.assertEqual(option.value, 120)

        # valuable dragon
        option = DiscardOption(player, HATSU, 0, [], 0)
        self.assertEqual(option.value, 120)

        # valuable dragon
        option = DiscardOption(player, CHUN, 0, [], 0)
        self.assertEqual(option.value, 120)

        player.dealer_seat = 0

        # double wind
        option = DiscardOption(player, EAST, 0, [], 0)
        self.assertEqual(option.value, 140)

    def test_calculate_suit_tiles_value_and_dora(self):
        table = Table()
        table.dora_indicators = [self._string_to_136_tile(sou='9')]
        player = Player(table, 0, 0, False)

        tile = self._string_to_34_tile(sou='1')
        option = DiscardOption(player, tile, 0, [], 0)
        self.assertEqual(option.value, 160)

        # double dora
        table.dora_indicators = [self._string_to_136_tile(sou='9'), self._string_to_136_tile(sou='9')]
        tile = self._string_to_34_tile(sou='1')
        option = DiscardOption(player, tile, 0, [], 0)
        self.assertEqual(option.value, 210)

    def test_discard_not_valuable_honor_first(self):
        table = Table()
        player = Player(table, 0, 0, False)

        tiles = self._string_to_136_array(sou='123456', pin='123456', man='9', honors='2')
        player.init_hand(tiles)

        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '2z')

    def test_slide_set_to_keep_dora_in_hand(self):
        table = Table()
        table.dora_indicators = [self._string_to_136_tile(pin='9')]
        player = Player(table, 0, 0, False)

        tiles = self._string_to_136_array(sou='123456', pin='23478', man='99')
        tile = self._string_to_136_tile(pin='1')
        player.init_hand(tiles)
        player.draw_tile(tile)

        # 2p is a dora, we had to keep it
        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '4p')

    def test_keep_aka_dora_in_hand(self):
        table = Table()
        table.dora_indicators = [self._string_to_136_tile(pin='1')]
        player = Player(table, 0, 0, False)

        tiles = self._string_to_136_array(sou='12346', pin='34578', man='99')
        # five sou, we can't get it from string (because from string it is always aka dora)
        tiles += [89]
        player.init_hand(tiles)
        player.draw_tile(FIVE_RED_SOU)

        # we had to keep red five and discard just 5s
        discarded_tile = player.discard_tile()
        self.assertNotEqual(discarded_tile, FIVE_RED_SOU)

    def test_dont_keep_honor_with_small_number_of_shanten(self):
        table = Table()
        player = Player(table, 0, 0, False)

        tiles = self._string_to_136_array(sou='11445', pin='55699', man='246')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors='7'))

        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '7z')
