# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.discard import DiscardOption
from mahjong.ai.main import MainAI
from mahjong.ai.shanten import Shanten
from mahjong.constants import EAST, SOUTH, WEST, NORTH, HAKU, HATSU, CHUN, FIVE_RED_SOU
from mahjong.player import Player
from mahjong.table import Table
from utils.tests import TestMixin


class CallRiichiTestCase(unittest.TestCase, TestMixin):

    def test_should_call_riichi_and_tanki_wait(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = Player(table, 0, 0, False)
        player.scores = 25000

        tiles = self._string_to_136_array(sou='123456', pin='12345', man='34')
        tile = self._string_to_136_tile(pin='6')
        player.init_hand(tiles)
        player.draw_tile(tile)
        player.discard_tile()

        self.assertEqual(player.can_call_riichi(), False)

        tiles = self._string_to_136_array(sou='1133557799', pin='113')
        tile = self._string_to_136_tile(pin='6')
        player.init_hand(tiles)
        player.draw_tile(tile)
        player.discard_tile()

        # for chitoitsu it is ok to have a pair wait
        self.assertEqual(player.can_call_riichi(), True)
