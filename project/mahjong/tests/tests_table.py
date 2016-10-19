# -*- coding: utf-8 -*-
import unittest

from mahjong.table import Table
from mahjong.tile import TilesConverter


class TableTestCase(unittest.TestCase):

    def test_init_hand(self):
        table = Table()
        tiles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        table.init_main_player_hand(tiles)

        self.assertEqual(len(table.get_main_player().tiles), 13)

    def test_init_round(self):
        table = Table()

        round_number = 4
        count_of_honba_sticks = 2
        count_of_riichi_sticks = 3
        dora_indicator = 126
        dealer = 3
        scores = [250, 250, 250, 250]

        table.init_round(round_number, count_of_honba_sticks, count_of_riichi_sticks, dora_indicator, dealer, scores)

        self.assertEqual(table.round_number, round_number)
        self.assertEqual(table.count_of_honba_sticks, count_of_honba_sticks)
        self.assertEqual(table.count_of_riichi_sticks, count_of_riichi_sticks)
        self.assertEqual(table.dora_indicators[0], dora_indicator)
        self.assertEqual(table.get_player(dealer).is_dealer, True)
        self.assertEqual(table.get_player(dealer).scores, 25000)

        dealer = 2
        table.get_main_player().in_tempai = True
        table.get_main_player().in_riichi = True
        table.init_round(round_number, count_of_honba_sticks, count_of_riichi_sticks, dora_indicator, dealer, scores)

        # test that we reinit round properly
        self.assertEqual(table.get_player(3).is_dealer, False)
        self.assertEqual(table.get_main_player().in_tempai, False)
        self.assertEqual(table.get_main_player().in_riichi, False)
        self.assertEqual(table.get_player(dealer).is_dealer, True)

    def test_set_scores(self):
        table = Table()
        table.init_round(0, 0, 0, 0, 0, [])
        scores = [230, 110, 55, 405]

        table.set_players_scores(scores)

        self.assertEqual(table.get_player(0).scores, 23000)
        self.assertEqual(table.get_player(1).scores, 11000)
        self.assertEqual(table.get_player(2).scores, 5500)
        self.assertEqual(table.get_player(3).scores, 40500)

    def test_set_scores_and_uma(self):
        table = Table()
        table.init_round(0, 0, 0, 0, 0, [])
        scores = [230, 110, 55, 405]
        uma = [-17, 3, 48, -34]

        table.set_players_scores(scores, uma)

        self.assertEqual(table.get_player(0).scores, 23000)
        self.assertEqual(table.get_player(0).uma, -17)
        self.assertEqual(table.get_player(1).scores, 11000)
        self.assertEqual(table.get_player(1).uma, 3)
        self.assertEqual(table.get_player(2).scores, 5500)
        self.assertEqual(table.get_player(2).uma, 48)
        self.assertEqual(table.get_player(3).scores, 40500)
        self.assertEqual(table.get_player(3).uma, -34)

    def test_set_scores_and_recalculate_player_position(self):
        table = Table()
        table.init_round(0, 0, 0, 0, 0, [])

        scores = [230, 110, 55, 405]
        table.set_players_scores(scores)

        self.assertEqual(table.get_player(0).position, 2)
        self.assertEqual(table.get_player(1).position, 3)
        self.assertEqual(table.get_player(2).position, 4)
        self.assertEqual(table.get_player(3).position, 1)

        scores = [110, 110, 405, 405]
        table.set_players_scores(scores)

        self.assertEqual(table.get_player(0).position, 3)
        self.assertEqual(table.get_player(1).position, 4)
        self.assertEqual(table.get_player(2).position, 1)
        self.assertEqual(table.get_player(3).position, 2)

    def test_set_names_and_ranks(self):
        table = Table()
        table.init_round(0, 0, 0, 0, 0, [])

        values = [
            {'name': 'NoName', 'rank': u'新人'},
            {'name': 'o2o2', 'rank': u'3級'},
            {'name': 'shimmmmm', 'rank': u'三段'},
            {'name': u'川海老', 'rank': u'9級'}
        ]

        table.set_players_names_and_ranks(values)

        self.assertEqual(table.get_player(0).name, 'NoName')
        self.assertEqual(table.get_player(0).rank, u'新人')
        self.assertEqual(table.get_player(3).name, u'川海老')
        self.assertEqual(table.get_player(3).rank, u'9級')

    def test_is_dora(self):
        table = Table()
        table.init_round(0, 0, 0, 0, 0, [])

        table.dora_indicators = [TilesConverter.string_to_136_array(sou='1')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(sou='2')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(sou='9')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(sou='1')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(pin='9')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(pin='1')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(man='9')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(man='1')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(man='5')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(man='6')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(honors='1')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(honors='2')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(honors='2')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(honors='3')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(honors='3')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(honors='4')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(honors='4')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(honors='1')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(honors='5')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(honors='6')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(honors='6')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(honors='7')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(honors='7')[0]]
        self.assertTrue(table.is_dora(TilesConverter.string_to_136_array(honors='5')[0]))

        table.dora_indicators = [TilesConverter.string_to_136_array(pin='1')[0]]
        self.assertFalse(table.is_dora(TilesConverter.string_to_136_array(sou='2')[0]))
