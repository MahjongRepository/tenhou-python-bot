# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.strategies.main import BaseStrategy
from mahjong.meld import Meld
from mahjong.player import Player
from mahjong.table import Table
from utils.tests import TestMixin


class AITestCase(unittest.TestCase, TestMixin):

    def test_set_is_tempai_flag_to_the_player(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(sou='111345677', pin='45', man='56')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        player.discard_tile()
        self.assertEqual(player.in_tempai, False)

        tiles = self._string_to_136_array(sou='11145677', pin='345', man='56')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        player.discard_tile()
        self.assertEqual(player.in_tempai, True)

    def test_not_open_hand_in_riichi(self):
        table = Table()
        player = Player(0, 0, table)

        player.in_riichi = True

        tiles = self._string_to_136_array(sou='12368', pin='2358', honors='4455')
        tile = self._string_to_136_tile(honors='5')
        player.init_hand(tiles)
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_chose_right_set_to_open_hand(self):
        """
        Different test cases to open hand and chose correct set to open hand.
        Based on real examples of incorrect opened hands
        """
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='23455', pin='3445678', honors='1')
        tile = self._string_to_136_tile(man='5')
        player.init_hand(tiles)
        meld, _, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(self._to_string(meld.tiles), '555m')

        tiles = self._string_to_136_array(man='335666', pin='22', sou='345', honors='55')
        tile = self._string_to_136_tile(man='4')
        player.init_hand(tiles)
        meld, _, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '345m')

        tiles = self._string_to_136_array(man='23557', pin='556788', honors='22')
        tile = self._string_to_136_tile(pin='5')
        player.init_hand(tiles)
        meld, _, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(self._to_string(meld.tiles), '555p')

    def test_not_open_hand_for_not_needed_set(self):
        """
        We don't need to open hand if it is not improve the hand.
        It was a bug related to it
        """
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='22457', sou='12234', pin='9', honors='55')
        tile = self._string_to_136_tile(sou='3')
        player.init_hand(tiles)
        meld, tile_to_discard, shanten = player.try_to_call_meld(tile, True)
        self.assertEqual(self._to_string(meld.tiles), '123s')
        player.add_called_meld(meld)
        player.discard_tile(tile_to_discard)
        player.ai.previous_shanten = shanten

        tile = self._string_to_136_tile(sou='3')
        meld, tile_to_discard, shanten = player.try_to_call_meld(tile, True)
        self.assertIsNone(meld)

    def test_chose_strategy_and_reset_strategy(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='33355788', sou='3479', honors='3')
        player.init_hand(tiles)
        self.assertEqual(player.ai.current_strategy.type, BaseStrategy.TANYAO)

        # we draw a tile that will change our selected strategy
        tile = self._string_to_136_tile(sou='8')
        player.draw_tile(tile)
        self.assertEqual(player.ai.current_strategy, None)

        tiles = self._string_to_136_array(man='33355788', sou='3479', honors='3')
        player.init_hand(tiles)
        self.assertEqual(player.ai.current_strategy.type, BaseStrategy.TANYAO)

        # for already opened hand we don't need to give up on selected strategy
        meld = Meld()
        meld.tiles = [1, 2, 3]
        player.add_called_meld(meld)
        tile = self._string_to_136_tile(sou='8')
        player.draw_tile(tile)
        self.assertEqual(player.ai.current_strategy.type, BaseStrategy.TANYAO)

    def test_remaining_tiles_and_enemy_discard(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='123456789', sou='167', honors='77')
        player.init_hand(tiles)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        self.assertEqual(results[0].tiles_count, 8)

        player.table.enemy_discard(self._string_to_136_tile(sou='5'), 1)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        self.assertEqual(results[0].tiles_count, 7)

        player.table.enemy_discard(self._string_to_136_tile(sou='5'), 2)
        player.table.enemy_discard(self._string_to_136_tile(sou='8'), 3)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        self.assertEqual(results[0].tiles_count, 5)

    def test_remaining_tiles_and_opened_meld(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='123456789', sou='167', honors='77')
        player.init_hand(tiles)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        self.assertEqual(results[0].tiles_count, 8)

        # was discard and set was opened
        tile = self._string_to_136_tile(sou='8')
        player.table.enemy_discard(tile, 3)
        meld = self._make_meld(Meld.PON, self._string_to_136_array(sou='888'))
        meld.called_tile = tile
        player.table.add_called_meld(meld, 3)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        self.assertEqual(results[0].tiles_count, 5)

        # was discard and set was opened
        tile = self._string_to_136_tile(sou='3')
        player.table.enemy_discard(tile, 2)
        meld = self._make_meld(Meld.PON, self._string_to_136_array(sou='345'))
        meld.called_tile = tile
        player.table.add_called_meld(meld, 2)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        self.assertEqual(results[0].tiles_count, 4)

    def test_remaining_tiles_and_dora_indicators(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='123456789', sou='167', honors='77')
        player.init_hand(tiles)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        self.assertEqual(results[0].tiles_count, 8)

        table.add_dora_indicator(self._string_to_136_tile(sou='8'))

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        self.assertEqual(results[0].tiles_count, 7)
