# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.main import MainAI
from mahjong.ai.shanten import Shanten
from mahjong.player import Player
from mahjong.table import Table
from utils.tests import TestMixin


class AITestCase(unittest.TestCase, TestMixin):

    def test_outs(self):
        table = Table()
        player = Player(0, table)
        ai = MainAI(table, player)

        tiles = self._string_to_136_array(sou='111345677', pin='15', man='56')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        outs, shanten = ai.calculate_outs()

        self.assertEqual(shanten, 2)
        self.assertEqual(outs[0]['discard'], 26)
        self.assertEqual(outs[0]['waiting'], [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 21, 24])
        self.assertEqual(outs[0]['tiles_count'], 57)

        tiles = self._string_to_136_array(sou='111345677', pin='45', man='56')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        outs, shanten = ai.calculate_outs()

        self.assertEqual(shanten, 1)
        self.assertEqual(outs[0]['discard'], 26)
        self.assertEqual(outs[0]['waiting'], [11, 14, 21, 24])
        self.assertEqual(outs[0]['tiles_count'], 16)

        tiles = self._string_to_136_array(sou='11145677', pin='345', man='56')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        outs, shanten = ai.calculate_outs()

        self.assertEqual(shanten, 0)
        self.assertEqual(outs[0]['discard'], 26)
        self.assertEqual(outs[0]['waiting'], [21, 24])
        self.assertEqual(outs[0]['tiles_count'], 8)

        tiles = self._string_to_136_array(sou='11145677', pin='345', man='56')
        tile = self._string_to_136_array(man='4')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        outs, shanten = ai.calculate_outs()

        self.assertEqual(shanten, Shanten.AGARI_STATE)
        self.assertEqual(len(outs), 0)

    def test_discard_tile(self):
        table = Table()
        player = Player(0, table)

        tiles = self._string_to_136_array(sou='111345677', pin='15', man='56')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 104)

        player.draw_tile(self._string_to_136_array(pin='4')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 36)

        player.draw_tile(self._string_to_136_array(pin='3')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 20)

        player.draw_tile(self._string_to_136_array(man='4')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, Shanten.AGARI_STATE)

    def test_discard_isolated_honor_tiles_first(self):
        table = Table()
        player = Player(0, table)

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
        player = Player(0, table)

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
