# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.defence import Defence
from mahjong.table import Table


class DefenceTestCase(unittest.TestCase):

    def test_go_to_the_defence_mode(self):
        table = Table()
        defence = Defence(table)

        self.assertFalse(defence.go_to_defence_mode())
        table.players[1].in_riichi = True
        self.assertTrue(defence.go_to_defence_mode())

        table.players[0].in_riichi = True
        self.assertFalse(defence.go_to_defence_mode())

    def test_calculate_safe_tiles_to_discard(self):
        table = Table()
        table.get_main_player().init_hand([3, 5, 6, 7, 8])
        defence = Defence(table)

        table.players[1].in_riichi = True
        table.players[1].add_discarded_tile(2)

        tile = defence.calculate_safe_tile_against_riichi()

        # 0, 1, 2, 3 - is a same tile
        self.assertEqual(tile, 3)
