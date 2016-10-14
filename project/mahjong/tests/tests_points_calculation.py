# -*- coding: utf-8 -*-
import unittest

from mahjong.hand import FinishedHand
from mahjong.tile import TilesConverter


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
