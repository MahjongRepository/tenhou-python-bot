# -*- coding: utf-8 -*-
import unittest

from mahjong.constants import EAST, SOUTH, WEST, NORTH
from mahjong.player import Player
from mahjong.table import Table


class PlayerTestCase(unittest.TestCase):

    def test_can_call_riichi_and_tempai(self):
        table = Table()
        player = Player(0, 0, table)

        player.in_tempai = False
        player.in_riichi = False
        player.scores = 2000
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.in_tempai = True

        self.assertEqual(player.can_call_riichi(), True)

    def test_can_call_riichi_and_already_in_riichi(self):
        table = Table()
        player = Player(0, 0, table)

        player.in_tempai = True
        player.in_riichi = True
        player.scores = 2000
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.in_riichi = False

        self.assertEqual(player.can_call_riichi(), True)

    def test_can_call_riichi_and_scores(self):
        table = Table()
        player = Player(0, 0, table)

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 0
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.scores = 1000

        self.assertEqual(player.can_call_riichi(), True)

    def test_can_call_riichi_and_remaining_tiles(self):
        table = Table()
        player = Player(0, 0, table)

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 2000
        player.table.count_of_remaining_tiles = 3

        self.assertEqual(player.can_call_riichi(), False)

        player.table.count_of_remaining_tiles = 5

        self.assertEqual(player.can_call_riichi(), True)

    def test_player_wind(self):
        table = Table()

        player = Player(0, 0, table)
        self.assertEqual(player.player_wind, EAST)

        player = Player(0, 1, table)
        self.assertEqual(player.player_wind, NORTH)

        player = Player(0, 2, table)
        self.assertEqual(player.player_wind, WEST)

        player = Player(0, 3, table)
        self.assertEqual(player.player_wind, SOUTH)
