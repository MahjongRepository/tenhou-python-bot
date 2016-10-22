# -*- coding: utf-8 -*-
import unittest

from mahjong.hand import FinishedHand
from utils.tests import TestMixin


class YakuCalculationTestCase(unittest.TestCase, TestMixin):

    def test_hand(self):
        hand = FinishedHand()

        # 123456789s11555z
        tiles = self._string_to_136_array(sou='123456789', honors='11555')
        win_tile = self._string_to_136_tile(sou='9')
        open_sets = [self._string_to_136_array(sou='456'), self._string_to_136_array(sou='555')]
        dora_indicators = [self._string_to_136_tile(sou='9')]
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True, open_sets=open_sets,
                                          dora_indicators=dora_indicators)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(result['han'], 5)
