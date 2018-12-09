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

    def test_is_threatening_and_two_open_yakuhai_melds(self):
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        # south player
        enemy_seat = 1
        # south round
        self.table.round_wind_number = 4

        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, honors='222'))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.CHI, man='123'))
        self.player.round_step = 2

        # double wind is not enough
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        # with one dora in enemy melds we can start think about threat
        # it will be 3 han
        self.table.add_dora_indicator(self._string_to_136_tile(man='1'))
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 1)
        self.assertEqual(threatening_players[0].player.seat, enemy_seat)

    def test_is_threatening_and_two_open_tanyao_melds(self):
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        enemy_seat = 2
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, pin='234'))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.CHI, sou='333'))
        self.player.round_step = 2

        # tanyao without dor is not threat
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        # and now it is threat
        self.table.add_dora_indicator(self._string_to_136_tile(pin='1'))
        self.table.add_dora_indicator(self._string_to_136_tile(pin='2'))
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 1)
        self.assertEqual(threatening_players[0].player.seat, enemy_seat)
