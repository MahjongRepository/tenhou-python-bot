# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.main import MainAI
from mahjong.ai.shanten import Shanten
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.ai.strategies.yakuhai import YakuhaiStrategy
from mahjong.meld import Meld
from mahjong.player import Player
from mahjong.table import Table
from utils.tests import TestMixin


class YakuhaiStrategyTestCase(unittest.TestCase, TestMixin):

    def test_should_activate_strategy(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)

        tiles = self._string_to_136_array(sou='12355689', man='89', honors='123')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='12355689', man='89', honors='44')
        player.init_hand(tiles)
        player.dealer_seat = 1
        self.assertEqual(strategy.should_activate_strategy(), True)

        tiles = self._string_to_136_array(sou='12355689', man='89', honors='666')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_suitable_tiles(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)

        # for yakuhai we can use any tile
        for tile in range(0, 136):
            self.assertEqual(strategy.is_tile_suitable(tile), True)

    def test_open_hand_with_yakuhai_pair_in_hand(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(sou='123678', pin='25899', honors='44')
        # 4 honor
        tile = 122
        player.init_hand(tiles)

        # we don't need to open hand with not our wind
        meld, _ = player.try_to_call_meld(tile, 3)
        self.assertEqual(meld, None)

        # with dragon pair in hand let's open our hand
        tiles = self._string_to_136_array(sou='1689', pin='2358', man='1', honors='4455')
        tile = 122
        player.init_hand(tiles)
        meld, _ = player.try_to_call_meld(tile, 3)
        self.assertNotEqual(meld, None)
        player.add_called_meld(meld)
        player.tiles.append(tile)

        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(meld.tiles, [120, 121, 122])
        self.assertEqual(len(player.closed_hand), 11)
        self.assertEqual(len(player.tiles), 14)
        player.discard_tile()

        tile = 126
        meld, _ = player.try_to_call_meld(tile, 3)
        self.assertNotEqual(meld, None)
        player.add_called_meld(meld)
        player.tiles.append(tile)

        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(meld.tiles, [124, 125, 126])
        self.assertEqual(len(player.closed_hand), 8)
        self.assertEqual(len(player.tiles), 14)
        player.discard_tile()

        tile = self._string_to_136_tile(sou='7')
        # we can call chi only from left player
        meld, _ = player.try_to_call_meld(tile, 2)
        self.assertEqual(meld, None)

        meld, _ = player.try_to_call_meld(tile, 3)
        self.assertNotEqual(meld, None)
        player.add_called_meld(meld)
        player.tiles.append(tile)

        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(meld.tiles, [92, 96, 100])
        self.assertEqual(len(player.closed_hand), 5)
        self.assertEqual(len(player.tiles), 14)
