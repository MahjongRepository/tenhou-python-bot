# -*- coding: utf-8 -*-
import unittest

from mahjong.tests_mixin import TestMixin
from mahjong.tile import Tile

from game.ai.first_version.strategies.main import BaseStrategy
from game.ai.first_version.strategies.formal_tempai import FormalTempaiStrategy
from game.table import Table


class FormalTempaiStrategyTestCase(unittest.TestCase, TestMixin):

    def setUp(self):
        self.table = Table()
        self.player = self.table.player
        self.player.dealer_seat = 3

    def test_should_activate_strategy(self):
        strategy = FormalTempaiStrategy(BaseStrategy.FORMAL_TEMPAI, self.player)

        tiles = self._string_to_136_array(sou='12355689', man='89', pin='339')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        # Let's move to 10th round step
        for i in range(0, 10):
            self.player.add_discarded_tile(Tile(0, False))

        self.assertEqual(strategy.should_activate_strategy(), False)

        # Now we move to 11th turn, we have 2 shanten and no doras,
        # we should go for formal tempai
        self.player.add_discarded_tile(Tile(0, True))
        self.assertEqual(strategy.should_activate_strategy(), True)
