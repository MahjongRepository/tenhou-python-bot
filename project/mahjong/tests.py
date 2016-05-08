import unittest

from mahjong.client import Client
from mahjong.meld import Meld
from mahjong.table import Table


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
        self.assertEqual(table.get_player(dealer).scores, 250)

    def test_set_scores(self):
        table = Table()
        table.init_round(0, 0, 0, 0, 0, [])
        scores = [230, 110, 55, 405]

        table.set_players_scores(scores)

        self.assertEqual(table.get_player(0).scores, 230)
        self.assertEqual(table.get_player(1).scores, 110)
        self.assertEqual(table.get_player(2).scores, 55)
        self.assertEqual(table.get_player(3).scores, 405)

    def test_set_scores_and_uma(self):
        table = Table()
        table.init_round(0, 0, 0, 0, 0, [])
        scores = [230, 110, 55, 405]
        uma = [-17, 3, 48, -34]

        table.set_players_scores(scores, uma)

        self.assertEqual(table.get_player(0).scores, 230)
        self.assertEqual(table.get_player(0).uma, -17)
        self.assertEqual(table.get_player(1).scores, 110)
        self.assertEqual(table.get_player(1).uma, 3)
        self.assertEqual(table.get_player(2).scores, 55)
        self.assertEqual(table.get_player(2).uma, 48)
        self.assertEqual(table.get_player(3).scores, 405)
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
        self.assertEqual(table.get_player(3).name, '川海老')
        self.assertEqual(table.get_player(3).rank, u'9級')


class ClientTestCase(unittest.TestCase):

    def test_draw_tile(self):
        client = Client()
        tiles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        client.table.init_main_player_hand(tiles)
        self.assertEqual(len(client.table.get_main_player().tiles), 13)

        client.draw_tile(14)

        self.assertEqual(len(client.table.get_main_player().tiles), 14)

    def test_discard_tile(self):
        client = Client()
        tiles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        client.table.init_main_player_hand(tiles)
        self.assertEqual(len(client.table.get_main_player().tiles), 14)

        tile = client.discard_tile()

        self.assertEqual(len(client.table.get_main_player().tiles), 13)
        self.assertEqual(len(client.table.get_main_player().discards), 1)
        self.assertFalse(tile in client.table.get_main_player().tiles)

    def test_call_meld(self):
        client = Client()

        meld = Meld()
        meld.who = 3

        client.call_meld(meld)

        self.assertEqual(len(client.table.get_player(3).melds), 1)

    def test_enemy_discard(self):
        client = Client()

        client.enemy_discard(1, 10)

        self.assertEqual(len(client.table.get_player(1).discards), 1)
