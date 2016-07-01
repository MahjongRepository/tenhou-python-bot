# -*- coding: utf-8 -*-
import unittest

from mahjong.client import Client
from mahjong.hand import FinishedHand
from mahjong.meld import Meld
from mahjong.player import Player
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


class ClientTestCase(unittest.TestCase):

    def test_draw_tile(self):
        client = Client()
        tiles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])
        client.table.init_main_player_hand(tiles)
        self.assertEqual(len(client.table.get_main_player().tiles), 13)
        self.assertEqual(client.table.count_of_remaining_tiles, 70)

        client.draw_tile(14)

        self.assertEqual(len(client.table.get_main_player().tiles), 14)
        self.assertEqual(client.table.count_of_remaining_tiles, 69)

    def test_discard_tile(self):
        client = Client()
        tiles = [1, 22, 3, 4, 43, 6, 7, 8, 9, 55, 11, 12, 13, 99]
        client.table.init_main_player_hand(tiles)
        self.assertEqual(len(client.table.get_main_player().tiles), 14)

        tile = client.discard_tile()

        self.assertEqual(len(client.table.get_main_player().tiles), 13)
        self.assertEqual(len(client.table.get_main_player().discards), 1)
        self.assertFalse(tile in client.table.get_main_player().tiles)

    def test_call_meld(self):
        client = Client()

        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])
        self.assertEqual(client.table.count_of_remaining_tiles, 70)

        meld = Meld()
        meld.who = 3

        client.call_meld(meld)

        self.assertEqual(len(client.table.get_player(3).melds), 1)
        self.assertEqual(client.table.count_of_remaining_tiles, 71)

    def test_enemy_discard(self):
        client = Client()
        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])

        self.assertEqual(client.table.count_of_remaining_tiles, 70)

        client.enemy_discard(1, 10)

        self.assertEqual(len(client.table.get_player(1).discards), 1)
        self.assertEqual(client.table.count_of_remaining_tiles, 69)


class TileTestCase(unittest.TestCase):

    def test_convert_to_one_line_string(self):
        tiles = [0, 1, 34, 35, 36, 37, 70, 71, 72, 73, 106, 107, 108, 109, 133, 134]
        result = TilesConverter.to_one_line_string(tiles)
        self.assertEqual('1199m1199p1199s1177z', result)

    def test_convert_to_34_array(self):
        tiles = [0, 34, 35, 36, 37, 70, 71, 72, 73, 106, 107, 108, 109, 134]
        result = TilesConverter.to_34_array(tiles)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[8], 2)
        self.assertEqual(result[9], 2)
        self.assertEqual(result[17], 2)
        self.assertEqual(result[18], 2)
        self.assertEqual(result[26], 2)
        self.assertEqual(result[27], 2)
        self.assertEqual(result[33], 1)
        self.assertEqual(sum(result), 14)

    def test_convert_string_to_136_array(self):
        tiles = TilesConverter.string_to_136_array(sou='19', pin='19', man='19', honors='1234567')

        self.assertEqual([0, 32, 36, 68, 72, 104, 108, 112, 116, 120, 124, 128, 132], tiles)

    def test_find_34_tile_in_136_array(self):
        result = TilesConverter.find_34_tile_in_136_array(0, [3, 4, 5, 6])
        self.assertEqual(result, 3)

        result = TilesConverter.find_34_tile_in_136_array(33, [3, 4, 134, 135])
        self.assertEqual(result, 134)

        result = TilesConverter.find_34_tile_in_136_array(20, [3, 4, 134, 135])
        self.assertEqual(result, None)


class PlayerTestCase(unittest.TestCase):

    def test_can_call_riichi_and_tempai(self):
        table = Table()
        player = Player(0, table)

        player.in_tempai = False
        player.in_riichi = False
        player.scores = 2000
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.in_tempai = True

        self.assertEqual(player.can_call_riichi(), True)


    def test_can_call_riichi_and_already_in_riichi(self):
        table = Table()
        player = Player(0, table)

        player.in_tempai = True
        player.in_riichi = True
        player.scores = 2000
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.in_riichi = False

        self.assertEqual(player.can_call_riichi(), True)

    def test_can_call_riichi_and_scores(self):
        table = Table()
        player = Player(0, table)

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 0
        player.table.count_of_remaining_tiles = 40

        self.assertEqual(player.can_call_riichi(), False)

        player.scores = 1000

        self.assertEqual(player.can_call_riichi(), True)

    def test_can_call_riichi_and_remaining_tiles(self):
        table = Table()
        player = Player(0, table)

        player.in_tempai = True
        player.in_riichi = False
        player.scores = 2000
        player.table.count_of_remaining_tiles = 3

        self.assertEqual(player.can_call_riichi(), False)

        player.table.count_of_remaining_tiles = 5

        self.assertEqual(player.can_call_riichi(), True)


class PointsCalculationTestCase(unittest.TestCase):

    def test_calculate_scores_and_ron(self):
        hand = FinishedHand()

        result = hand.calculate_scores(han=1, fu=30, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 1000)

        result = hand.calculate_scores(han=1, fu=110, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 3600)

        result = hand.calculate_scores(han=2, fu=30, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 2000)

        result = hand.calculate_scores(han=3, fu=30, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 3900)

        result = hand.calculate_scores(han=4, fu=30, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 7700)

        result = hand.calculate_scores(han=4, fu=40, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 8000)

        result = hand.calculate_scores(han=4, fu=40, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 12000)

        result = hand.calculate_scores(han=5, fu=0, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 8000)

        result = hand.calculate_scores(han=6, fu=0, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 12000)

        result = hand.calculate_scores(han=8, fu=0, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 16000)

        result = hand.calculate_scores(han=11, fu=0, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 24000)

        result = hand.calculate_scores(han=13, fu=0, is_tsumo=False, is_dealer=False)
        self.assertEqual(result['main'], 32000)

    def test_calculate_scores_and_ron_by_dealer(self):
        hand = FinishedHand()

        result = hand.calculate_scores(han=1, fu=30, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 1500)

        result = hand.calculate_scores(han=2, fu=30, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 2900)

        result = hand.calculate_scores(han=3, fu=30, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 5800)

        result = hand.calculate_scores(han=4, fu=30, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 11600)

        result = hand.calculate_scores(han=5, fu=0, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 12000)

        result = hand.calculate_scores(han=6, fu=0, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 18000)

        result = hand.calculate_scores(han=8, fu=0, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 24000)

        result = hand.calculate_scores(han=11, fu=0, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 36000)

        result = hand.calculate_scores(han=13, fu=0, is_tsumo=False, is_dealer=True)
        self.assertEqual(result['main'], 48000)

    def test_calculate_scores_and_tsumo(self):
        hand = FinishedHand()

        result = hand.calculate_scores(han=1, fu=30, is_tsumo=True, is_dealer=False)
        self.assertEqual(result['main'], 500)
        self.assertEqual(result['additional'], 300)

        result = hand.calculate_scores(han=3, fu=30, is_tsumo=True, is_dealer=False)
        self.assertEqual(result['main'], 2000)
        self.assertEqual(result['additional'], 1000)

        result = hand.calculate_scores(han=4, fu=30, is_tsumo=True, is_dealer=False)
        self.assertEqual(result['main'], 3900)
        self.assertEqual(result['additional'], 2000)

        result = hand.calculate_scores(han=5, fu=0, is_tsumo=True, is_dealer=False)
        self.assertEqual(result['main'], 4000)
        self.assertEqual(result['additional'], 2000)

        result = hand.calculate_scores(han=6, fu=0, is_tsumo=True, is_dealer=False)
        self.assertEqual(result['main'], 6000)
        self.assertEqual(result['additional'], 3000)

        result = hand.calculate_scores(han=8, fu=0, is_tsumo=True, is_dealer=False)
        self.assertEqual(result['main'], 8000)
        self.assertEqual(result['additional'], 4000)

        result = hand.calculate_scores(han=11, fu=0, is_tsumo=True, is_dealer=False)
        self.assertEqual(result['main'], 12000)
        self.assertEqual(result['additional'], 6000)

        result = hand.calculate_scores(han=13, fu=0, is_tsumo=True, is_dealer=False)
        self.assertEqual(result['main'], 16000)
        self.assertEqual(result['additional'], 8000)

    def test_pinfu_hand_and_riichi(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='123456', man='12345', pin='55')
        win_tile = TilesConverter.string_to_136_array(man='6')[0]
        self.assertTrue(hand.is_pinfu(tiles, win_tile))

        # waiting in two pairs
        tiles = TilesConverter.string_to_136_array(sou='123456', man='12355', pin='55')
        win_tile = TilesConverter.string_to_136_array(man='5')[0]
        self.assertFalse(hand.is_pinfu(tiles, win_tile))

        # contains pon or kan
        tiles = TilesConverter.string_to_136_array(sou='111456', man='12345', pin='55')
        win_tile = TilesConverter.string_to_136_array(man='6')[0]
        self.assertFalse(hand.is_pinfu(tiles, win_tile))

        tiles = TilesConverter.string_to_136_array(sou='12345', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(result['cost'], {'main': 2000, 'additional': 0})
        self.assertEqual(len(result['hand_yaku']), 2)

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True, is_riichi=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 3)
        self.assertEqual(result['fu'], 20)
        self.assertEqual(result['cost'], {'main': 1300, 'additional': 700})
        self.assertEqual(len(result['hand_yaku']), 3)

    def test_is_chitoitsu_hand(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='113355', man='113355', pin='11')
        self.assertTrue(hand.is_chitoitsu(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='2299', man='2299', pin='1199', honors='44')
        self.assertTrue(hand.is_chitoitsu(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='113355', man='113355', pin='1')
        win_tile = TilesConverter.string_to_136_array(pin='1')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 3)
        self.assertEqual(result['fu'], 25)
        self.assertEqual(result['cost'], {'main': 3200, 'additional': 0})
        self.assertEqual(len(result['hand_yaku']), 2)

    def test_is_tanyao(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='234567', man='234567', pin='22')
        self.assertTrue(hand.is_tanyao(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='123456', man='234567', pin='22')
        self.assertFalse(hand.is_tanyao(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='234567', honors='22')
        self.assertFalse(hand.is_tanyao(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23456', pin='22')
        win_tile = TilesConverter.string_to_136_array(man='7')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 3)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(result['cost'], {'main': 3900, 'additional': 0})
        self.assertEqual(len(result['hand_yaku']), 3)

    def test_is_pinfu_hand(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='123456', man='12345', pin='55')
        win_tile = TilesConverter.string_to_136_array(man='6')[0]
        self.assertTrue(hand.is_pinfu(tiles, win_tile))

        # waiting in two pairs
        tiles = TilesConverter.string_to_136_array(sou='123456', man='12355', pin='55')
        win_tile = TilesConverter.string_to_136_array(man='5')[0]
        self.assertFalse(hand.is_pinfu(tiles, win_tile))

        # contains pon or kan
        tiles = TilesConverter.string_to_136_array(sou='111456', man='12345', pin='55')
        win_tile = TilesConverter.string_to_136_array(man='6')[0]
        self.assertFalse(hand.is_pinfu(tiles, win_tile))

    def test_is_haku(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='555')
        self.assertTrue(hand.is_haku(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='55')
        win_tile = TilesConverter.string_to_136_array(honors='5')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(result['cost'], {'main': 1000, 'additional': 0})
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_hatsu(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='666')
        self.assertTrue(hand.is_hatsu(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='66')
        win_tile = TilesConverter.string_to_136_array(honors='6')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(result['cost'], {'main': 1000, 'additional': 0})
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_chun(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='777')
        self.assertTrue(hand.is_chun(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='77')
        win_tile = TilesConverter.string_to_136_array(honors='7')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(result['cost'], {'main': 1000, 'additional': 0})
        self.assertEqual(len(result['hand_yaku']), 1)
