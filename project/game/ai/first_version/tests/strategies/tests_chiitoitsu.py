# -*- coding: utf-8 -*-
import unittest

from mahjong.tests_mixin import TestMixin

from game.ai.first_version.strategies.chiitoitsu import ChiitoitsuStrategy
from game.ai.first_version.strategies.main import BaseStrategy
from game.table import Table


class ChiitoitsuStrategyTestCase(unittest.TestCase, TestMixin):

    def test_should_activate_strategy(self):
        table = Table()
        player = table.player
        strategy = ChiitoitsuStrategy(BaseStrategy.CHIITOITSU, player)

        # obvious chiitoitsu, let's activate
        tiles = self._string_to_136_array(sou='2266', man='3399', pin='289', honors='116')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        # less than 5 pairs, don't activate
        tiles = self._string_to_136_array(sou='2266', man='3389', pin='289', honors='116')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # 5 pairs, but we are already tempai, let's no consider this hand as chiitoitsu
        tiles = self._string_to_136_array(sou='234', man='223344', pin='55669')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        tiles = self._string_to_136_array(sou='234', man='22334455669')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

    def test_dont_call_meld(self):
        table = Table()
        player = table.player
        strategy = ChiitoitsuStrategy(BaseStrategy.CHIITOITSU, player)

        tiles = self._string_to_136_array(sou='112234', man='2334499')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        tile = self._string_to_136_tile(man='9')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)
