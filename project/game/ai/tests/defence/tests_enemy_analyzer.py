# -*- coding: utf-8 -*-
import unittest

from game.ai.defence.yaku_analyzer.honitsu import HonitsuAnalyzer
from game.ai.defence.yaku_analyzer.tanyao import TanyaoAnalyzer
from game.ai.defence.yaku_analyzer.yakuhai import YakuhaiAnalyzer
from game.table import Table
from mahjong.constants import HONOR_INDICES, TERMINAL_INDICES
from mahjong.meld import Meld
from mahjong.tests_mixin import TestMixin


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
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, man="333"))
        self.player.round_step = 7

        # simple pon it is no threat
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        # dora pon it is threat
        self.table.add_dora_indicator(self._string_to_136_tile(man="2"))
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

        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, honors="222"))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.CHI, man="123"))
        self.player.round_step = 2

        # double wind is not enough
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        # with one dora in enemy melds we can start think about threat
        # it will be 3 han
        self.table.add_dora_indicator(self._string_to_136_tile(man="1"))
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 1)
        self.assertEqual(threatening_players[0].player.seat, enemy_seat)

    def test_is_threatening_and_two_open_tanyao_melds(self):
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        enemy_seat = 2
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, pin="234"))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.CHI, sou="333"))
        self.player.round_step = 2

        # tanyao without dor is not threat
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        # and now it is threat
        self.table.add_dora_indicator(self._string_to_136_tile(pin="1"))
        self.table.add_dora_indicator(self._string_to_136_tile(pin="2"))
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 1)
        self.assertEqual(threatening_players[0].player.seat, enemy_seat)

    def test_is_threatening_and_honitsu_hand(self):
        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 0)

        enemy_seat = 1
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, pin="567"))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.CHI, pin="123"))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.CHI, pin="345"))

        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(sou="1"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(sou="5"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(sou="8"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(sou="9"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(man="1"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(man="1"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(pin="1"), False)

        threatening_players = self.player.ai.defence._get_threatening_players()
        self.assertEqual(len(threatening_players), 1)

    def test_tanyao_dangerous_tiles(self):
        tanyao = TanyaoAnalyzer(self.table.player)
        dangerous_tiles = tanyao.get_dangerous_tiles()

        self.assertEqual(len(dangerous_tiles), 21)
        self.assertEqual(all([x in TERMINAL_INDICES for x in dangerous_tiles]), False)
        self.assertEqual(all([x in HONOR_INDICES for x in dangerous_tiles]), False)

    def test_yakuhai_dangerous_tiles(self):
        yakuhai = YakuhaiAnalyzer(self.table.player)
        dangerous_tiles = yakuhai.get_dangerous_tiles()

        self.assertEqual(len(dangerous_tiles), 34)

    def test_honitsu_dangerous_tiles(self):
        enemy_seat = 2
        honitsu = HonitsuAnalyzer(self.table.get_player(enemy_seat))

        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.PON, pin="567"))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.CHI, pin="123"))
        self.table.add_called_meld(enemy_seat, self._make_meld(Meld.CHI, pin="345"))

        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(sou="1"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(sou="5"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(sou="8"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(sou="9"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(man="1"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(man="1"), False)
        self.table.add_discarded_tile(enemy_seat, self._string_to_136_tile(pin="1"), False)

        self.assertTrue(honitsu.is_yaku_active())
        dangerous_tiles = honitsu.get_dangerous_tiles()

        # 9 from suit
        # 7 from honors
        self.assertEqual(len(dangerous_tiles), 16)

    # def test_detect_enemy_tempai_and_riichi(self):
    #     table = Table()
    #
    #     self.assertEqual(EnemyAnalyzer(None, table.get_player(1)).in_tempai, False)
    #     self.assertEqual(EnemyAnalyzer(None, table.get_player(1)).is_threatening, False)
    #
    #     table.add_called_riichi(1)
    #
    #     self.assertEqual(EnemyAnalyzer(None, table.get_player(1)).in_tempai, True)
    #     self.assertEqual(EnemyAnalyzer(None, table.get_player(1)).is_threatening, True)
    #
    #
