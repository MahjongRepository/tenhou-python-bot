# -*- coding: utf-8 -*-
import unittest

from mahjong.constants import EAST, NORTH, WEST, SOUTH
from mahjong.meld import Meld
from mahjong.tests_mixin import TestMixin

from game.player import Player
from game.table import Table
from utils.settings_handler import settings


class PlayerTestCase(unittest.TestCase, TestMixin):

    def test_can_call_riichi_and_tempai(self):
        table = Table()
        player = table.player

        player.in_tempai = False
        player.in_riichi = False
        player.scores = 2000
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.formal_riichi_conditions(), False)

        player.in_tempai = True

        self.assertEqual(player.formal_riichi_conditions(), True)

    def test_can_call_riichi_and_already_in_riichi(self):
        table = Table()
        player = table.player

        player.in_tempai = True
        player.in_riichi = True
        player.scores = 2000
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.formal_riichi_conditions(), False)

        player.in_riichi = False

        self.assertEqual(player.formal_riichi_conditions(), True)

    def test_can_call_riichi_and_scores(self):
        table = Table()
        player = table.player

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 0
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.formal_riichi_conditions(), False)

        player.scores = 1000

        self.assertEqual(player.formal_riichi_conditions(), True)

    def test_can_call_riichi_and_remaining_tiles(self):
        table = Table()
        player = table.player

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 2000
        player.table.count_of_remaining_tiles = 3

        self.assertEqual(player.formal_riichi_conditions(), False)

        player.table.count_of_remaining_tiles = 5

        self.assertEqual(player.formal_riichi_conditions(), True)

    def test_can_call_riichi_and_open_hand(self):
        table = Table()
        player = table.player

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 2000
        player.melds = [Meld()]
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.formal_riichi_conditions(), False)

        player.melds = []

        self.assertEqual(player.formal_riichi_conditions(), True)

    def test_player_wind(self):
        table = Table()

        player = table.player
        self.assertEqual(player.player_wind, EAST)

        player = Player(table, 0, 1)
        self.assertEqual(player.player_wind, NORTH)

        player = Player(table, 0, 2)
        self.assertEqual(player.player_wind, WEST)

        player = Player(table, 0, 3)
        self.assertEqual(player.player_wind, SOUTH)

    def test_player_called_meld_and_closed_hand(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou='123678', pin='3599', honors='555')
        player.init_hand(tiles)

        self.assertEqual(len(player.closed_hand), 13)

        player.add_called_meld(self._make_meld(Meld.PON, honors='555'))

        self.assertEqual(len(player.closed_hand), 10)
