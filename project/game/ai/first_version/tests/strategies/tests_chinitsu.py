# -*- coding: utf-8 -*-
import unittest

from mahjong.tests_mixin import TestMixin

from game.ai.first_version.strategies.chinitsu import ChinitsuStrategy
from game.ai.first_version.strategies.main import BaseStrategy
from game.table import Table


class ChinitsuStrategyTestCase(unittest.TestCase, TestMixin):

    def test_should_activate_strategy(self):
        table = Table()
        player = table.player
        strategy = ChinitsuStrategy(BaseStrategy.CHINITSU, player)

        table.add_dora_indicator(self._string_to_136_tile(pin='1'))
        table.add_dora_indicator(self._string_to_136_tile(man='1'))
        table.add_dora_indicator(self._string_to_136_tile(sou='8'))

        tiles = self._string_to_136_array(sou='12355', man='34589', honors='123')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        tiles = self._string_to_136_array(sou='12355', man='458', honors='11234')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # we shouldn't go for chinitsu if we have a valued pair or pon
        tiles = self._string_to_136_array(sou='111222578', man='8', honors='555')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        tiles = self._string_to_136_array(sou='1112227788', man='7', honors='55')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # if we have a pon of non-valued honors, this is not chinitsu
        tiles = self._string_to_136_array(sou='1112224688', honors='222')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # if we have just a pair of non-valued tiles, we can go for chinitsu
        # if we have 11 chinitsu tiles and it's early
        tiles = self._string_to_136_array(sou='11122234688', honors='22')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        # if we have a complete set with dora, we shouldn't go for chinitsu
        tiles = self._string_to_136_array(sou='1112223688', pin='123')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # even if the set may be interpreted as two forms
        tiles = self._string_to_136_array(sou='111223688', pin='2334')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # even if the set may be interpreted as two forms v2
        tiles = self._string_to_136_array(sou='111223688', pin='2345')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # if we have a long form with dora, we shouldn't go for chinitsu
        tiles = self._string_to_136_array(sou='111223688', pin='2333')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # buf it it's just a ryanmen - no problem
        tiles = self._string_to_136_array(sou='1112223688', pin='238')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        # we have three non-isolated doras in other suits, this is not chinitsu
        tiles = self._string_to_136_array(sou='111223688', man='22', pin='23')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # we have two non-isolated doras in other suits and no doras in our suit
        # this is not chinitsu
        tiles = self._string_to_136_array(sou='111223688', man='24', pin='24')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # we have two non-isolated doras in other suits and 1 shanten, not chinitsu
        tiles = self._string_to_136_array(sou='111222789', man='23', pin='23')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

    def test_suitable_tiles(self):
        table = Table()
        player = table.player
        strategy = ChinitsuStrategy(BaseStrategy.CHINITSU, player)

        tiles = self._string_to_136_array(sou='111222479', man='78', honors='12')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        tile = self._string_to_136_tile(man='1')
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(pin='1')
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(strategy.is_tile_suitable(tile), True)

        tile = self._string_to_136_tile(honors='1')
        self.assertEqual(strategy.is_tile_suitable(tile), False)
