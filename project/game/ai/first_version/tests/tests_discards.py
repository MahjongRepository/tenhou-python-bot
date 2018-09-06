# -*- coding: utf-8 -*-
import unittest

from mahjong.constants import EAST, SOUTH, WEST, NORTH, HAKU, HATSU, CHUN, FIVE_RED_SOU, FIVE_RED_PIN
from mahjong.tests_mixin import TestMixin
from mahjong.meld import Meld

from game.ai.discard import DiscardOption
from game.ai.first_version.strategies.main import BaseStrategy
from game.ai.first_version.strategies.tanyao import TanyaoStrategy
from game.table import Table


class DiscardLogicTestCase(unittest.TestCase, TestMixin):

    def test_discard_tile(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou='11134567', pin='159', man='45')
        tile = self._string_to_136_tile(man='9')
        player.init_hand(tiles)
        player.draw_tile(tile)

        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '9m')
        self.assertEqual(player.ai.shanten, 2)

        player.draw_tile(self._string_to_136_tile(pin='4'))
        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '1p')
        self.assertEqual(player.ai.shanten, 2)

        player.draw_tile(self._string_to_136_tile(pin='3'))
        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '9p')
        self.assertEqual(player.ai.shanten, 1)

        player.draw_tile(self._string_to_136_tile(man='4'))
        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '5m')
        self.assertEqual(player.ai.shanten, 0)

    def test_discard_tile_force_tsumogiri(self):
        table = Table()
        table.has_aka_dora = True
        player = table.player

        tiles = self._string_to_136_array(sou='11134567', pin='456', man='45')
        # 6p
        tile = 57

        player.init_hand(tiles)
        player.draw_tile(tile)

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, tile)

        # add not red five pin
        tiles = self._string_to_136_array(sou='11134567', pin='46', man='45') + [53]
        tile = FIVE_RED_PIN

        player.init_hand(tiles)
        player.draw_tile(tile)

        discarded_tile = player.discard_tile()
        # WE DON'T NEED TO DISCARD RED FIVE
        self.assertNotEqual(discarded_tile, tile)

    def test_calculate_suit_tiles_value(self):
        table = Table()
        player = table.player

        # 0 - 8   man
        # 9 - 17  pin
        # 18 - 26 sou
        results = [
            [0, 110], [9,  110], [18, 110],
            [1, 120], [10, 120], [19, 120],
            [2, 140], [11, 140], [20, 140],
            [3, 150], [12, 150], [21, 150],
            [4, 130], [13, 130], [22, 130],
            [5, 150], [14, 150], [23, 150],
            [6, 140], [15, 140], [24, 140],
            [7, 120], [16, 120], [25, 120],
            [8, 110], [17, 110], [26, 110]
        ]

        for item in results:
            tile = item[0]
            value = item[1]
            option = DiscardOption(player, tile, 0, [], 0)
            self.assertEqual(option.valuation, value)

    def test_calculate_suit_tiles_value_and_tanyao_hand(self):
        table = Table()
        player = table.player
        player.ai.current_strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        # 0 - 8   man
        # 9 - 17  pin
        # 18 - 26 sou
        results = [
            [0, 110], [9,  110], [18, 110],
            [1, 120], [10, 120], [19, 120],
            [2, 130], [11, 130], [20, 130],
            [3, 150], [12, 150], [21, 150],
            [4, 140], [13, 140], [22, 140],
            [5, 150], [14, 150], [23, 150],
            [6, 130], [15, 130], [24, 130],
            [7, 120], [16, 120], [25, 120],
            [8, 110], [17, 110], [26, 110]
        ]

        for item in results:
            tile = item[0]
            value = item[1]
            option = DiscardOption(player, tile, 0, [], 0)
            self.assertEqual(option.valuation, value)

    def test_calculate_honor_tiles_value(self):
        table = Table()
        player = table.player
        player.dealer_seat = 3

        # valuable honor, wind of the round
        option = DiscardOption(player, EAST, 0, [], 0)
        self.assertEqual(option.valuation, 120)

        # valuable honor, wind of the player
        option = DiscardOption(player, SOUTH, 0, [], 0)
        self.assertEqual(option.valuation, 120)

        # not valuable wind
        option = DiscardOption(player, WEST, 0, [], 0)
        self.assertEqual(option.valuation, 100)

        # not valuable wind
        option = DiscardOption(player, NORTH, 0, [], 0)
        self.assertEqual(option.valuation, 100)

        # valuable dragon
        option = DiscardOption(player, HAKU, 0, [], 0)
        self.assertEqual(option.valuation, 120)

        # valuable dragon
        option = DiscardOption(player, HATSU, 0, [], 0)
        self.assertEqual(option.valuation, 120)

        # valuable dragon
        option = DiscardOption(player, CHUN, 0, [], 0)
        self.assertEqual(option.valuation, 120)

        player.dealer_seat = 0

        # double wind
        option = DiscardOption(player, EAST, 0, [], 0)
        self.assertEqual(option.valuation, 140)

    def test_calculate_suit_tiles_value_and_dora(self):
        table = Table()
        table.dora_indicators = [self._string_to_136_tile(sou='9')]
        player = table.player

        tile = self._string_to_34_tile(sou='1')
        option = DiscardOption(player, tile, 0, [], 0)
        self.assertEqual(option.valuation, DiscardOption.DORA_VALUE + 110)

        # double dora
        table.dora_indicators = [self._string_to_136_tile(sou='9'), self._string_to_136_tile(sou='9')]
        tile = self._string_to_34_tile(sou='1')
        option = DiscardOption(player, tile, 0, [], 0)
        self.assertEqual(option.valuation, DiscardOption.DORA_VALUE * 2 + 110)

        # tile close to dora
        table.dora_indicators = [self._string_to_136_tile(sou='9')]
        tile = self._string_to_34_tile(sou='2')
        option = DiscardOption(player, tile, 0, [], 0)
        self.assertEqual(option.valuation, DiscardOption.DORA_FIRST_NEIGHBOUR + 120)

        # tile not far away from dora
        table.dora_indicators = [self._string_to_136_tile(sou='9')]
        tile = self._string_to_34_tile(sou='3')
        option = DiscardOption(player, tile, 0, [], 0)
        self.assertEqual(option.valuation, DiscardOption.DORA_SECOND_NEIGHBOUR + 140)

    def test_discard_not_valuable_honor_first(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou='123456', pin='123456', man='9', honors='2')
        player.init_hand(tiles)

        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '2z')

    def test_slide_set_to_keep_dora_in_hand(self):
        table = Table()
        table.dora_indicators = [self._string_to_136_tile(pin='9')]
        player = table.player

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
        table.has_aka_dora = True
        player = table.player

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
        player = table.player

        tiles = self._string_to_136_array(sou='11445', pin='55699', man='246')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors='7'))

        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '7z')

    def test_prefer_valuable_tiles_with_almost_same_ukeire(self):
        table = Table()
        player = table.player
        table.add_dora_indicator(self._string_to_136_tile(sou='4'))

        tiles = self._string_to_136_array(sou='1366', pin='123456', man='345')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(sou='5'))

        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '1s')

    def test_discard_less_valuable_isolated_tile_first(self):
        table = Table()
        player = table.player
        table.add_dora_indicator(self._string_to_136_tile(sou='4'))

        tiles = self._string_to_136_array(sou='2456', pin='129', man='234458')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(sou='7'))

        discarded_tile = player.discard_tile()
        # we have a choice what to discard: 9p or 8m
        # 9p is less valuable
        self.assertEqual(self._to_string([discarded_tile]), '9p')

        table.dora_indicators.append(self._string_to_136_tile(pin='8'))
        tiles = self._string_to_136_array(sou='2456', pin='129', man='234458')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(sou='7'))
        discarded_tile = player.discard_tile()
        # but if 9p is dora
        # let's discard 8m instead
        self.assertEqual(self._to_string([discarded_tile]), '8m')

    def test_discard_tile_with_max_ukeire_second_level(self):
        table = Table()
        player = table.player
        table.add_dora_indicator(self._string_to_136_tile(sou='4'))

        tiles = self._string_to_136_array(sou='11367', pin='45', man='344778')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(pin='6'))

        discarded_tile = player.discard_tile()
        self.assertEqual(self._to_string([discarded_tile]), '3s')

    # There was a bug with count of live tiles that are used in melds,
    # hence this test
    def test_choose_best_option_with_melds(self):
        table = Table()
        player = table.player
        table.has_aka_dora = False

        tiles = self._string_to_136_array(sou='245666789', honors='2266')
        player.init_hand(tiles)

        meld = self._make_meld(Meld.PON, sou='666')
        player.add_called_meld(meld)
        meld = self._make_meld(Meld.CHI, sou='789')
        player.add_called_meld(meld)

        player.draw_tile(self._string_to_136_tile(sou='5'))

        discarded_tile = player.discard_tile()
        # we should discard best ukeire option here - 2s
        self.assertEqual(self._to_string([discarded_tile]), '2s')

    def test_choose_best_wait_with_melds(self):
        table = Table()
        player = table.player
        table.has_aka_dora = False

        tiles = self._string_to_136_array(sou='1222233455599')
        player.init_hand(tiles)

        meld = self._make_meld(Meld.CHI, sou='123')
        player.add_called_meld(meld)
        meld = self._make_meld(Meld.PON, sou='222')
        player.add_called_meld(meld)
        meld = self._make_meld(Meld.PON, sou='555')
        player.add_called_meld(meld)

        player.draw_tile(self._string_to_136_tile(sou='4'))

        discarded_tile = player.discard_tile()
        # double-pairs wait becomes better, because it has 4 tiles to wait for
        # against just 1 in ryanmen
        self.assertEqual(self._to_string([discarded_tile]), '3s')
