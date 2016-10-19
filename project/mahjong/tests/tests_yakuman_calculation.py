# -*- coding: utf-8 -*-
import unittest

from mahjong.hand import FinishedHand, HandDivider
from mahjong.tile import TilesConverter


class YakumanCalculationTestCase(unittest.TestCase):

    def _string_to_open_34_set(self, sou='', pin='', man='', honors=''):
        open_set = TilesConverter.string_to_136_array(sou=sou, pin=pin, man=man, honors=honors)
        open_set[0] //= 4
        open_set[1] //= 4
        open_set[2] //= 4
        return open_set

    def _string_to_34_tile(self, sou='', pin='', man='', honors=''):
        item = TilesConverter.string_to_136_array(sou=sou, pin=pin, man=man, honors=honors)
        item[0] //= 4
        return item[0]

    def test_is_tenhou(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tenhou=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_chiihou(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_chiihou=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_daisangen(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='123', man='22', honors='555666777')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_daisangen(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(sou='123', man='22', honors='55566677')
        win_tile = TilesConverter.string_to_136_array(honors='7')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 60)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_shosuushi(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='123', honors='11122233344')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_shosuushi(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(sou='123', honors='1112223334')
        win_tile = TilesConverter.string_to_136_array(honors='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 60)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_daisuushi(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='22', honors='111222333444')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_daisuushi(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(sou='22', honors='11122233344')
        win_tile = TilesConverter.string_to_136_array(honors='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 26)
        self.assertEqual(result['fu'], 70)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_tsuisou(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(honors='11122233366677')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_tsuisou(hand_tiles[0]))

        tiles = TilesConverter.string_to_34_array(honors='11223344556677')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_tsuisou(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(honors='1122334455667')
        win_tile = TilesConverter.string_to_136_array(honors='7')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 25)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_chinroto(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='111999', man='111999', pin='99')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_chinroto(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(sou='111222', man='111999', pin='9')
        win_tile = TilesConverter.string_to_136_array(pin='9')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 26)
        self.assertEqual(result['fu'], 60)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_kokushi(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='119', man='19', pin='19', honors='1234567')
        self.assertTrue(hand.is_kokushi(tiles))

        tiles = TilesConverter.string_to_136_array(sou='11', man='19', pin='19', honors='1234567')
        win_tile = TilesConverter.string_to_136_array(sou='9')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

        tiles = TilesConverter.string_to_136_array(sou='19', man='19', pin='19', honors='1234567')
        win_tile = TilesConverter.string_to_136_array(sou='1')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 26)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_ryuisou(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='22334466888', honors='666')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_ryuisou(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(sou='22334466888', honors='66')
        win_tile = TilesConverter.string_to_136_array(honors='6')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_suuankou(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='111444', man='333', pin='44555')
        hand_tiles = hand_divider.divide_hand(tiles)
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        self.assertTrue(hand.is_suuankou(win_tile, hand_tiles[0], True))
        self.assertFalse(hand.is_suuankou(win_tile, hand_tiles[0], False))

        tiles = TilesConverter.string_to_136_array(sou='111444', man='333', pin='4455')
        win_tile = TilesConverter.string_to_136_array(pin='5')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False)
        self.assertNotEqual(result['han'], 13)

        tiles = TilesConverter.string_to_136_array(sou='111444', man='333', pin='4445')
        win_tile = TilesConverter.string_to_136_array(pin='5')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 26)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_chuuren_poutou(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(man='11122345678999')
        win_tile = TilesConverter.string_to_136_array(man='2')[0]
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_chuuren_poutou(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(man='1122345678999')
        win_tile = TilesConverter.string_to_136_array(man='1')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 1)

        tiles = TilesConverter.string_to_136_array(man='1112345678999')
        win_tile = TilesConverter.string_to_136_array(man='2')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 26)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_suukantsu(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='111333', man='222', pin='44555')
        hand_tiles = hand_divider.divide_hand(tiles)
        called_kan_indices = [self._string_to_34_tile(sou='1'), self._string_to_34_tile(sou='3'),
                              self._string_to_34_tile(pin='5'), self._string_to_34_tile(man='2')]
        self.assertTrue(hand.is_suukantsu(hand_tiles[0], called_kan_indices))

        tiles = TilesConverter.string_to_136_array(sou='111333', man='222', pin='4555')
        win_tile = TilesConverter.string_to_136_array(pin='4')[0]
        open_sets = [self._string_to_open_34_set(sou='111'), self._string_to_open_34_set(sou='333')]

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=open_sets, called_kan_indices=called_kan_indices)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 13)
        self.assertEqual(result['fu'], 90)
        self.assertEqual(len(result['hand_yaku']), 1)
