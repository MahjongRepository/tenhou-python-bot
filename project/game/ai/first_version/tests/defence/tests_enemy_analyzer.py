# -*- coding: utf-8 -*-
import unittest

from mahjong.meld import Meld
from mahjong.tests_mixin import TestMixin

from game.table import Table


class EnemyAnalyzerTestCase(unittest.TestCase, TestMixin):

    def setUp(self):
        self.table = Table()
        self.player = self.table.player

    def test_is_threatening_in_riichi(self):
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        enemy_seat = 2
        self.table.add_called_riichi(enemy_seat)

        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 1)
        self.assertEqual(threatening_players[0].player.seat, enemy_seat)

    def test_is_threatening_and_dora_pon(self):
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        enemy_seat = 2
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, man='333'))
        self.player.round_step = 7

        # simple pon it is no threat
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        # dora pon it is threat
        self.table.add_dora_indicator(self._string_to_136_tile(man='2'))
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 1)
        self.assertEqual(threatening_players[0].player.seat, enemy_seat)

    def test_is_threatening_and_two_open_melds_with_dora(self):
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        enemy_seat = 2
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, man='333'))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, man='333'))
        self.player.round_step = 2

        self.table.add_dora_indicator(self._string_to_136_tile(man='2'))

        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 1)
        self.assertEqual(threatening_players[0].player.seat, enemy_seat)

    def test_is_threatening_and_two_open_melds_and_yakuhai_melds(self):
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        enemy_seat = 2
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, honors='222'))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.CHI, man='123'))
        self.player.round_step = 2

        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        self.table.add_dora_indicator(self._string_to_136_tile(man='1'))

        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 1)
        self.assertEqual(threatening_players[0].player.seat, enemy_seat)
