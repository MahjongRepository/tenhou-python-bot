# -*- coding: utf-8 -*-
import unittest

from mahjong.tests_mixin import TestMixin
from mahjong.tile import Tile
from mahjong.meld import Meld

from game.ai.first_version.strategies.formal_tempai import FormalTempaiStrategy
from game.ai.first_version.strategies.main import BaseStrategy
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
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        # Let's move to 10th round step
        for _ in range(0, 10):
            self.player.add_discarded_tile(Tile(0, False))

        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        # Now we move to 11th turn, we have 2 shanten and no doras,
        # we should go for formal tempai
        self.player.add_discarded_tile(Tile(0, True))
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), True)

    def test_get_tempai(self):
        tiles = self._string_to_136_array(man='2379', sou='4568', pin='22299')
        self.player.init_hand(tiles)

        # Let's move to 15th round step
        for _ in range(0, 15):
            self.player.add_discarded_tile(Tile(0, False))

        tile = self._string_to_136_tile(man='8')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string(meld.tiles), '789m')

        tile_to_discard = self.player.discard_tile()
        self.assertEqual(self._to_string([tile_to_discard]), '8s')

    # we shouldn't open when we are already in tempai expect for some
    # special cases
    def test_dont_meld_agari(self):
        strategy = FormalTempaiStrategy(BaseStrategy.FORMAL_TEMPAI, self.player)

        tiles = self._string_to_136_array(man='2379', sou='4568', pin='22299')
        self.player.init_hand(tiles)

        # Let's move to 15th round step
        for _ in range(0, 15):
            self.player.add_discarded_tile(Tile(0, False))

        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), True)

        tiles = self._string_to_136_array(man='23789', sou='456', pin='22299')
        self.player.init_hand(tiles)

        meld = self._make_meld(Meld.CHI, man='789')
        self.player.add_called_meld(meld)

        tile = self._string_to_136_tile(man='4')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)
