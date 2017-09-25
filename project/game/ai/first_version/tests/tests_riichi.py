# -*- coding: utf-8 -*-
import unittest

from mahjong.tests_mixin import TestMixin

from game.table import Table


class CallRiichiTestCase(unittest.TestCase, TestMixin):

    def test_dont_call_riichi_with_tanki_wait(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        tiles = self._string_to_136_array(sou='123456', pin='123456', man='3')
        player.init_hand(tiles)

        player.draw_tile(self._string_to_136_tile(man='4'))
        player.discard_tile()

        self.assertEqual(player.can_call_riichi(), False)

        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        tiles = self._string_to_136_array(sou='1133557799', pin='113')
        tile = self._string_to_136_tile(pin='6')
        player.init_hand(tiles)
        player.draw_tile(tile)
        player.discard_tile()

        # for chitoitsu it is ok to have a pair wait
        self.assertEqual(player.can_call_riichi(), True)

    def test_call_riichi_and_penchan_wait(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        tiles = self._string_to_136_array(sou='11223', pin='234567', man='66')
        tile = self._string_to_136_tile(man='9')
        player.init_hand(tiles)
        player.draw_tile(tile)
        player.discard_tile()

        self.assertEqual(player.can_call_riichi(), True)
