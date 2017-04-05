# -*- coding: utf-8 -*-
import unittest

from mahjong.meld import Meld
from mahjong.table import Table
from mahjong.utils import is_pin
from utils.tests import TestMixin


class EnemyAnalyzerTestCase(unittest.TestCase, TestMixin):

    def test_detect_enemy_tempai_and_riichi(self):
        table = Table()

        self.assertEqual(table.get_player(1).in_tempai, False)
        self.assertEqual(table.get_player(1).is_threatening, False)

        table.add_called_riichi(1)

        self.assertEqual(table.get_player(1).in_tempai, True)
        self.assertEqual(table.get_player(1).is_threatening, True)

    def test_detect_enemy_tempai_and_opened_sets(self):
        table = Table()

        self.assertEqual(table.get_player(1).in_tempai, False)
        self.assertEqual(table.get_player(1).is_threatening, False)

        table.add_called_meld(1, self._make_meld(Meld.CHI, self._string_to_136_array(sou='567')))
        table.add_called_meld(1, self._make_meld(Meld.CHI, self._string_to_136_array(pin='123')))
        table.add_called_meld(1, self._make_meld(Meld.CHI, self._string_to_136_array(man='345')))
        table.add_called_meld(1, self._make_meld(Meld.PON, self._string_to_136_array(man='777')))

        self.assertEqual(table.get_player(1).in_tempai, True)
        self.assertEqual(table.get_player(1).is_threatening, False)

        table.dora_indicators = [self._string_to_136_tile(man='6')]

        # enemy opened the pon of dor, so better to fold against him
        self.assertEqual(table.get_player(1).in_tempai, True)
        self.assertEqual(table.get_player(1).is_threatening, True)

    def test_try_to_detect_honitsu_hand(self):
        table = Table()

        table.add_called_meld(1, self._make_meld(Meld.CHI, self._string_to_136_array(pin='567')))
        table.add_called_meld(1, self._make_meld(Meld.CHI, self._string_to_136_array(pin='123')))
        table.add_called_meld(1, self._make_meld(Meld.CHI, self._string_to_136_array(pin='345')))

        table.add_discarded_tile(1, self._string_to_136_tile(sou='1'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(sou='5'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(sou='8'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(sou='9'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(man='1'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(man='1'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='1'), False)

        self.assertEqual(table.get_player(1).is_threatening, True)
        self.assertEqual(table.get_player(1).chosen_suit, is_pin)
