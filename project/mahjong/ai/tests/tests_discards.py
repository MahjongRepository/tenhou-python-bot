# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.main import MainAI
from mahjong.ai.shanten import Shanten
from mahjong.player import Player
from mahjong.table import Table
from utils.tests import TestMixin


class DiscardLogicTestCase(unittest.TestCase, TestMixin):

    def test_outs(self):
        table = Table()
        player = Player(0, 0, table)
        ai = MainAI(table, player)

        tiles = self._string_to_136_array(sou='111345677', pin='15', man='569')
        player.init_hand(tiles)
        outs, shanten = ai.calculate_outs(tiles, tiles, False)

        self.assertEqual(shanten, 2)
        tile = self._to_string([outs[0].find_tile_in_hand(player.closed_hand)])
        self.assertEqual(tile, '9m')
        self.assertEqual(outs[0].waiting, [3, 6, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 24, 25])
        self.assertEqual(outs[0].tiles_count, 57)

        tiles = self._string_to_136_array(sou='111345677', pin='145', man='56')
        player.init_hand(tiles)
        outs, shanten = ai.calculate_outs(tiles, tiles, False)

        self.assertEqual(shanten, 1)
        tile = self._to_string([outs[0].find_tile_in_hand(player.closed_hand)])
        self.assertEqual(tile, '1p')
        self.assertEqual(outs[0].waiting, [3, 6, 11, 14])
        self.assertEqual(outs[0].tiles_count, 16)

        tiles = self._string_to_136_array(sou='111345677', pin='345', man='56')
        player.init_hand(tiles)
        outs, shanten = ai.calculate_outs(tiles, tiles, False)

        self.assertEqual(shanten, 0)
        tile = self._to_string([outs[0].find_tile_in_hand(player.closed_hand)])
        self.assertEqual(tile, '3s')
        self.assertEqual(outs[0].waiting, [3, 6])
        self.assertEqual(outs[0].tiles_count, 8)

        tiles = self._string_to_136_array(sou='11145677', pin='345', man='456')
        outs, shanten = ai.calculate_outs(tiles, tiles, False)

        self.assertEqual(shanten, Shanten.AGARI_STATE)
        self.assertEqual(len(outs), 0)

    def test_discard_tile(self):
        table = Table()
        player = Player(0, 0, table)

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
