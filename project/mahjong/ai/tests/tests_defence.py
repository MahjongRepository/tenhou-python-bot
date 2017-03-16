# -*- coding: utf-8 -*-
import unittest

from mahjong.table import Table
from utils.tests import TestMixin


class DefenceTestCase(unittest.TestCase, TestMixin):

    def test_add_safe_tile_after_discard(self):
        table = Table()
        table.add_called_riichi(3)

        table.add_discarded_tile(1, self._string_to_136_tile(man='3'), False)

        self.assertEqual(len(table.get_player(1).discards), 1)
        self.assertEqual(len(table.get_player(2).discards), 0)
        self.assertEqual(len(table.get_player(3).discards), 0)

        self.assertEqual(len(table.get_player(1).safe_tiles), 1)
        self.assertEqual(len(table.get_player(2).safe_tiles), 0)
        self.assertEqual(len(table.get_player(3).safe_tiles), 1)

        # "2" is 3 man
        self.assertEqual(table.get_player(1).safe_tiles[0], 2)
        self.assertEqual(table.get_player(3).safe_tiles[0], 2)

    def test_temporary_safe_tiles(self):
        table = Table()

        table.add_discarded_tile(1, self._string_to_136_tile(man='4'), False)

        self.assertEqual(table.get_player(1).temporary_safe_tiles, [])
        self.assertEqual(table.get_player(2).temporary_safe_tiles, [3])
        self.assertEqual(table.get_player(3).temporary_safe_tiles, [3])

        table.add_discarded_tile(2, self._string_to_136_tile(man='5'), False)

        self.assertEqual(table.get_player(1).temporary_safe_tiles, [4])
        self.assertEqual(table.get_player(2).temporary_safe_tiles, [])
        self.assertEqual(table.get_player(3).temporary_safe_tiles, [3, 4])

        table.add_discarded_tile(3, self._string_to_136_tile(man='6'), False)

        self.assertEqual(table.get_player(1).temporary_safe_tiles, [4, 5])
        self.assertEqual(table.get_player(2).temporary_safe_tiles, [5])
        self.assertEqual(table.get_player(3).temporary_safe_tiles, [])

        table.add_discarded_tile(1, self._string_to_136_tile(man='7'), False)

        self.assertEqual(table.get_player(1).temporary_safe_tiles, [])
        self.assertEqual(table.get_player(2).temporary_safe_tiles, [5, 6])
        self.assertEqual(table.get_player(3).temporary_safe_tiles, [6])

    def test_should_go_for_defence_and_bad_hand(self):
        table = Table()

        tiles = self._string_to_136_array(sou='1259', pin='12348', honors='3456')
        table.player.init_hand(tiles)
        table.player.draw_tile(self._string_to_136_tile(man='6'))
        # discard here to reinit shanten number in AI
        table.player.discard_tile()

        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), False)

        table.add_called_riichi(3)

        # our hand is pretty bad, there is no sense to push it against riichi
        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), True)

    def test_should_go_for_defence_and_good_hand(self):
        table = Table()

        tiles = self._string_to_136_array(sou='234567', pin='34789', man='55')
        table.player.init_hand(tiles)
        table.player.draw_tile(self._string_to_136_tile(man='6'))
        # discard here to reinit shanten number in AI
        table.player.discard_tile()

        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), False)

        table.add_called_riichi(3)

        # our hand is in tempai, but it is really cheap
        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), True)

        table.add_dora_indicator(self._string_to_136_tile(man='4'))
        table.add_dora_indicator(self._string_to_136_tile(pin='3'))

        # our hand in tempai, and it has a cost, so let's push it
        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), False)

    def test_find_common_safe_tile_to_discard(self):
        table = Table()

        tiles = self._string_to_136_array(sou='2345678', pin='34789', man='55')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(man='4'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(man='5'), False)

        table.add_discarded_tile(2, self._string_to_136_tile(man='5'), False)
        table.add_discarded_tile(2, self._string_to_136_tile(man='6'), False)

        table.add_called_riichi(1)
        table.add_called_riichi(2)

        # for this test we don't need temporary_safe_tiles
        table.get_player(1).temporary_safe_tiles = []
        table.get_player(2).temporary_safe_tiles = []

        result = table.player.discard_tile()

        self.assertEqual(self._to_string([result]), '5m')

    def test_find_dealer_tile_to_discard(self):
        dealer = 2
        table = Table()
        table.init_round(0, 0, 0, 0, dealer, [])

        tiles = self._string_to_136_array(sou='2345678', pin='34', man='55789')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(man='4'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(man='5'), False)

        table.add_discarded_tile(2, self._string_to_136_tile(man='8'), False)
        table.add_discarded_tile(2, self._string_to_136_tile(man='9'), False)

        table.add_called_riichi(1)
        table.add_called_riichi(2)

        # for this test we don't need temporary_safe_tiles
        table.get_player(1).temporary_safe_tiles = []
        table.get_player(2).temporary_safe_tiles = []

        result = table.player.discard_tile()

        # second player is a dealer, let's fold against him
        self.assertEqual(self._to_string([result]), '8m')

    def test_try_to_discard_not_needed_tiles_first_in_defence_mode(self):
        table = Table()

        tiles = self._string_to_136_array(sou='2345678', pin='789', man='55', honors='12')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(man='5'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(honors='1'), False)

        table.add_called_riichi(1)

        result = table.player.discard_tile()

        self.assertEqual(self._to_string([result]), '1z')
