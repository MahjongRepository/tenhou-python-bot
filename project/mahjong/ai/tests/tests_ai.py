# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.main import MainAI
from mahjong.ai.shanten import Shanten
from mahjong.meld import Meld
from mahjong.player import Player
from mahjong.table import Table
from utils.tests import TestMixin


class AITestCase(unittest.TestCase, TestMixin):

    def test_outs(self):
        table = Table()
        player = Player(0, 0, table)
        ai = MainAI(table, player)

        tiles = self._string_to_136_array(sou='111345677', pin='15', man='569')
        outs, shanten = ai.calculate_outs(tiles, tiles)

        self.assertEqual(shanten, 2)
        self.assertEqual(outs[0]['discard'], 9)
        self.assertEqual(outs[0]['waiting'], [3, 6, 7, 8, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24, 25])
        self.assertEqual(outs[0]['tiles_count'], 57)

        tiles = self._string_to_136_array(sou='111345677', pin='45', man='569')
        outs, shanten = ai.calculate_outs(tiles, tiles)

        self.assertEqual(shanten, 1)
        self.assertEqual(outs[0]['discard'], 23)
        self.assertEqual(outs[0]['waiting'], [3, 6, 11, 14])
        self.assertEqual(outs[0]['tiles_count'], 16)

        tiles = self._string_to_136_array(sou='11145677', pin='345', man='569')
        outs, shanten = ai.calculate_outs(tiles, tiles)

        self.assertEqual(shanten, 0)
        self.assertEqual(outs[0]['discard'], 8)
        self.assertEqual(outs[0]['waiting'], [3, 6])
        self.assertEqual(outs[0]['tiles_count'], 8)

        tiles = self._string_to_136_array(sou='11145677', pin='345', man='456')
        outs, shanten = ai.calculate_outs(tiles, tiles)

        self.assertEqual(shanten, Shanten.AGARI_STATE)
        self.assertEqual(len(outs), 0)

    def test_discard_tile(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(sou='111345677', pin='15', man='56')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 36)

        player.draw_tile(self._string_to_136_array(pin='4')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 92)

        player.draw_tile(self._string_to_136_array(pin='3')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 32)

        player.draw_tile(self._string_to_136_array(man='4')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, Shanten.AGARI_STATE)

    def test_discard_isolated_honor_tiles_first(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(sou='8', pin='56688', man='11323', honors='36')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 128)

        player.draw_tile(self._string_to_136_array(man='4')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 116)

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
        meld, _ = player.try_to_call_meld(tile, 3)
        self.assertEqual(meld, None)
