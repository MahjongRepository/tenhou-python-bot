# -*- coding: utf-8 -*-
import unittest

from mahjong.constants import EAST, SOUTH, WEST, NORTH
from mahjong.meld import Meld
from mahjong.player import Player
from mahjong.table import Table
from utils.tests import TestMixin


class PlayerTestCase(unittest.TestCase, TestMixin):

    def test_can_call_riichi_and_tempai(self):
        table = Table()
        player = Player(table, 0, 0, False)

        player.in_tempai = False
        player.in_riichi = False
        player.scores = 2000
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.in_tempai = True

        self.assertEqual(player.can_call_riichi(), True)

    def test_can_call_riichi_and_already_in_riichi(self):
        table = Table()
        player = Player(table, 0, 0, False)

        player.in_tempai = True
        player.in_riichi = True
        player.scores = 2000
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.in_riichi = False

        self.assertEqual(player.can_call_riichi(), True)

    def test_can_call_riichi_and_scores(self):
        table = Table()
        player = Player(table, 0, 0, False)

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 0
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.scores = 1000

        self.assertEqual(player.can_call_riichi(), True)

    def test_can_call_riichi_and_remaining_tiles(self):
        table = Table()
        player = Player(table, 0, 0, False)

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 2000
        player.table.count_of_remaining_tiles = 3

        self.assertEqual(player.can_call_riichi(), False)

        player.table.count_of_remaining_tiles = 5

        self.assertEqual(player.can_call_riichi(), True)

    def test_can_call_riichi_and_open_hand(self):
        table = Table()
        player = Player(table, 0, 0, False)

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 2000
        player.melds = [1]
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.melds = []

        self.assertEqual(player.can_call_riichi(), True)

    def test_player_wind(self):
        table = Table()

        player = Player(table, 0, 0, False)
        self.assertEqual(player.player_wind, EAST)

        player = Player(table, 0, 1, False)
        self.assertEqual(player.player_wind, NORTH)

        player = Player(table, 0, 2, False)
        self.assertEqual(player.player_wind, WEST)

        player = Player(table, 0, 3, False)
        self.assertEqual(player.player_wind, SOUTH)

    def test_player_called_meld_and_closed_hand(self):
        table = Table()
        player = Player(table, 0, 0, False)

        tiles = self._string_to_136_array(sou='123678', pin='3599', honors='555')
        player.init_hand(tiles)

        meld_tiles = [124, 125, 126]

        self.assertEqual(len(player.closed_hand), 13)

        player.add_called_meld(self._make_meld(Meld.PON, meld_tiles))

        self.assertEqual(len(player.closed_hand), 10)
