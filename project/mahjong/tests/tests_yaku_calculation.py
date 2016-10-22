# -*- coding: utf-8 -*-
import unittest

from mahjong.hand import FinishedHand, HandDivider
from mahjong.constants import EAST, SOUTH, WEST, NORTH, FIVE_RED_SOU
from utils.tests import TestMixin
from utils.settings_handler import settings


class YakuCalculationTestCase(unittest.TestCase, TestMixin):

    def tearDown(self):
        settings.FIVE_REDS = False

    def test_hand_dividing(self):
        hand = HandDivider()

        tiles_34 = self._string_to_34_array(man='234567', sou='23455', honors='777')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [[1, 2, 3], [4, 5, 6], [19, 20, 21], [22, 22], [33, 33, 33]])

        tiles_34 = self._string_to_34_array(man='123', pin='123', sou='123', honors='11222')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [[0, 1, 2], [9, 10, 11], [18, 19, 20], [27, 27], [28, 28, 28]])

        tiles_34 = self._string_to_34_array(man='23444', pin='344556', sou='333')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [[1, 2, 3], [3, 3], [11, 12, 13], [12, 13, 14], [20, 20, 20]])

        tiles_34 = self._string_to_34_array(man='11122233388899')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [[0, 1, 2], [0, 1, 2], [0, 1, 2], [7, 7, 7], [8, 8]])
        self.assertEqual(result[1], [[0, 0, 0], [1, 1, 1], [2, 2, 2], [7, 7, 7], [8, 8]])

        tiles_34 = self._string_to_34_array(man='112233', sou='445566', pin='99')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [[0, 1, 2], [0, 1, 2], [17, 17], [21, 22, 23], [21, 22, 23]])
        self.assertEqual(result[1], [[0, 0], [1, 1], [2, 2], [17, 17], [21, 21], [22, 22], [23, 23]])

    def test_fu_calculation(self):
        hand = FinishedHand()
        player_wind, round_wind = EAST, WEST

        tiles = self._string_to_136_array(sou='123678', man='123456', pin='22')
        win_tile = self._string_to_136_tile(sou='6')
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False)
        self.assertEqual(result['fu'], 30)
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True)
        self.assertEqual(result['fu'], 20)

        tiles = self._string_to_136_array(pin='112233999', honors='11177')
        win_tile = self._string_to_136_tile(pin='9')
        open_sets = [self._string_to_136_array(honors='111'), self._string_to_136_array(pin='123'),
                     self._string_to_136_array(pin='123')]

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=open_sets)
        self.assertEqual(result['fu'], 30)

        # if we can't ad pinfu to the hand hand
        # we can add 2 fu to make hand more expensive
        tiles = self._string_to_136_array(sou='678', man='11', pin='123345', honors='666')
        win_tile = self._string_to_136_tile(pin='3')
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True)
        self.assertEqual(result['fu'], 40)

        tiles = self._string_to_136_array(man='234789', pin='12345666')
        win_tile = self._string_to_136_tile(pin='6')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['fu'], 30)

        tiles = self._string_to_136_array(sou='678', pin='34555789', honors='555')
        win_tile = self._string_to_136_tile(pin='5')
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True)
        self.assertEqual(result['fu'], 40)

        # penchan 1-2-... waiting
        tiles = self._string_to_136_array(sou='12456', man='123456', pin='55')
        win_tile = self._string_to_136_tile(sou='3')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # penchan ...-8-9 waiting
        tiles = self._string_to_136_array(sou='34589', man='123456', pin='55')
        win_tile = self._string_to_136_tile(sou='7')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # kanchan waiting
        tiles = self._string_to_136_array(sou='12357', man='123456', pin='55')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # valued pair
        tiles = self._string_to_136_array(sou='12378', man='123456', honors='11')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # pair waiting
        tiles = self._string_to_136_array(sou='123678', man='123456', pin='1')
        win_tile = self._string_to_136_tile(pin='1')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # pon
        tiles = self._string_to_136_array(sou='22278', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(4, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # pon and ron on tile
        tiles = self._string_to_136_array(sou='22678', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='2')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # open pon
        tiles = self._string_to_136_array(sou='22278', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        open_sets = [self._string_to_open_34_set(sou='222')]
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind,
                                                         open_sets, []))

        # kan
        tiles = self._string_to_136_array(sou='22278', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        called_kan_indices = [self._string_to_34_tile(sou='2')]
        self.assertEqual(16, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [],
                                                          called_kan_indices))

        # open kan
        tiles = self._string_to_136_array(sou='22278', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        called_kan_indices = [self._string_to_34_tile(sou='2')]
        open_sets = [self._string_to_open_34_set(sou='222')]
        self.assertEqual(8, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, open_sets,
                                                         called_kan_indices))

        # terminal pon
        tiles = self._string_to_136_array(sou='11178', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(8, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # terminal pon and ron on tile
        tiles = self._string_to_136_array(sou='11678', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='1')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(4, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # open terminal pon
        tiles = self._string_to_136_array(sou='11178', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        open_sets = [self._string_to_open_34_set(sou='111')]
        self.assertEqual(4, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind,
                                                         open_sets, []))

        # terminal kan
        tiles = self._string_to_136_array(sou='11178', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        called_kan_indices = [self._string_to_34_tile(sou='1')]
        self.assertEqual(32, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [],
                                                          called_kan_indices))

        # open terminal kan
        tiles = self._string_to_136_array(sou='11178', man='123456', pin='11')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        called_kan_indices = [self._string_to_34_tile(sou='1')]
        open_sets = [self._string_to_open_34_set(sou='111')]
        self.assertEqual(16, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, open_sets,
                                                          called_kan_indices))

        # honor pon
        tiles = self._string_to_136_array(sou='78', man='123456', pin='11', honors='111')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        self.assertEqual(8, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [], []))

        # open honor pon
        tiles = self._string_to_136_array(sou='78', man='123456', pin='11', honors='111')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        open_sets = [self._string_to_open_34_set(honors='111')]
        self.assertEqual(4, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind,
                                                         open_sets, []))

        # honor kan
        tiles = self._string_to_136_array(sou='78', man='123456', pin='11', honors='111')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        called_kan_indices = [self._string_to_34_tile(honors='1')]
        self.assertEqual(32, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, [],
                                                          called_kan_indices))

        # open honor kan
        tiles = self._string_to_136_array(sou='78', man='123456', pin='11', honors='111')
        win_tile = self._string_to_136_tile(sou='6')
        hand_tiles = self._hand(self._to_34_array(tiles + [win_tile]), 0)
        called_kan_indices = [self._string_to_34_tile(honors='1')]
        open_sets = [self._string_to_open_34_set(honors='111')]
        self.assertEqual(16, hand.calculate_additional_fu(win_tile, hand_tiles, False, player_wind, round_wind, open_sets,
                                                          called_kan_indices))

    def test_is_riichi(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123444', man='234456', pin='66')
        win_tile = self._string_to_136_tile(sou='4')

        result = hand.estimate_hand_value(tiles, win_tile, is_riichi=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, is_riichi=True, open_sets=[[0, 1, 2]])
        self.assertNotEqual(result['error'], None)

    def test_is_tsumo(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123444', man='234456', pin='66')
        win_tile = self._string_to_136_tile(sou='4')

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

        # with open hand tsumo not giving yaku
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True, open_sets=[[0, 1, 2]])
        self.assertNotEqual(result['error'], None)

    def test_is_ippatsu(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123444', man='234456', pin='66')
        win_tile = self._string_to_136_tile(sou='4')

        result = hand.estimate_hand_value(tiles, win_tile, is_riichi=True, is_ippatsu=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 2)

        # without riichi ippatsu is not possible
        result = hand.estimate_hand_value(tiles, win_tile, is_riichi=False, is_ippatsu=True)
        self.assertNotEqual(result['error'], None)

    def test_is_rinshan(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123444', man='234456', pin='66')
        win_tile = self._string_to_136_tile(sou='4')

        result = hand.estimate_hand_value(tiles, win_tile, is_rinshan=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_chankan(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123444', man='234456', pin='66')
        win_tile = self._string_to_136_tile(sou='4')

        result = hand.estimate_hand_value(tiles, win_tile, is_chankan=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_haitei(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123444', man='234456', pin='66')
        win_tile = self._string_to_136_tile(sou='4')

        result = hand.estimate_hand_value(tiles, win_tile, is_haitei=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_houtei(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123444', man='234456', pin='66')
        win_tile = self._string_to_136_tile(sou='4')

        result = hand.estimate_hand_value(tiles, win_tile, is_houtei=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_renhou(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123444', man='234456', pin='66')
        win_tile = self._string_to_136_tile(sou='4')

        result = hand.estimate_hand_value(tiles, win_tile, is_renhou=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 5)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_daburu_riichi(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123444', man='234456', pin='66')
        win_tile = self._string_to_136_tile(sou='4')

        result = hand.estimate_hand_value(tiles, win_tile, is_daburu_riichi=True, is_riichi=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_nagashi_mangan(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='13579', man='234456', pin='66')

        result = hand.estimate_hand_value(tiles, None, is_nagashi_mangan=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 5)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_chitoitsu_hand(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='113355', man='113355', pin='11')
        self.assertTrue(hand.is_chitoitsu(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='2299', man='2299', pin='1199', honors='44')
        self.assertTrue(hand.is_chitoitsu(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='113355', man='113355', pin='11')
        win_tile = self._string_to_136_tile(pin='1')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 25)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_tanyao(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='234567', man='234567', pin='22')
        self.assertTrue(hand.is_tanyao(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='123456', man='234567', pin='22')
        self.assertFalse(hand.is_tanyao(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='234567', man='234567', honors='22')
        self.assertFalse(hand.is_tanyao(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='234567', man='234567', pin='22')
        win_tile = self._string_to_136_tile(man='7')

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 3)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 3)

        tiles = self._string_to_136_array(sou='234567', man='234567', pin='22')
        win_tile = self._string_to_136_tile(man='7')
        open_sets = [self._string_to_136_array(sou='234')]
        result = hand.estimate_hand_value(tiles, win_tile, open_sets=open_sets)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_pinfu_hand(self):
        player_wind, round_wind = EAST, WEST
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123456', man='123456', pin='55')
        win_tile = self._string_to_136_tile(man='6')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

        # waiting in two pairs
        tiles = self._string_to_136_array(sou='123456', man='123555', pin='55')
        win_tile = self._string_to_136_tile(man='5')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertNotEqual(result['error'], None)

        # contains pon or kan
        tiles = self._string_to_136_array(sou='111456', man='123456', pin='55')
        win_tile = self._string_to_136_tile(man='6')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertNotEqual(result['error'], None)

        # penchan waiting
        tiles = self._string_to_136_array(sou='123456', man='123456', pin='55')
        win_tile = self._string_to_136_tile(sou='3')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertNotEqual(result['error'], None)

        # kanchan waiting
        tiles = self._string_to_136_array(sou='123567', man='123456', pin='55')
        win_tile = self._string_to_136_tile(sou='6')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertNotEqual(result['error'], None)

        # tanki waiting
        tiles = self._string_to_136_array(man='22456678', pin='123678')
        win_tile = self._string_to_136_tile(man='2')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertNotEqual(result['error'], None)

        # valued pair
        tiles = self._string_to_136_array(sou='123678', man='123456', honors='11')
        win_tile = self._string_to_136_tile(sou='6')
        result = hand.estimate_hand_value(tiles, win_tile, player_wind=player_wind, round_wind=round_wind)
        self.assertNotEqual(result['error'], None)

        # not valued pair
        tiles = self._string_to_136_array(sou='123678', man='123456', honors='22')
        win_tile = self._string_to_136_tile(sou='6')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

        tiles = self._string_to_136_array(sou='123345678', man='678', pin='88')
        win_tile = self._string_to_136_tile(sou='3')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

        tiles = self._string_to_136_array(sou='12399', man='123456', pin='456')
        win_tile = self._string_to_136_tile(sou='1')
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

        # open hand
        tiles = self._string_to_136_array(sou='12399', man='123456', pin='456')
        win_tile = self._string_to_136_tile(sou='1')
        open_sets = [self._string_to_136_array(sou='123')]
        result = hand.estimate_hand_value(tiles, win_tile, open_sets=open_sets)
        self.assertNotEqual(result['error'], None)

    def test_is_iipeiko(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='112233', man='123', pin='23444')
        self.assertTrue(hand.is_iipeiko(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='112233', man='333', pin='12344')
        win_tile = self._string_to_136_tile(man='3')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=[[0, 1, 2]])
        self.assertNotEqual(result['error'], None)

    def test_is_ryanpeiko(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='112233', man='22', pin='223344')
        self.assertTrue(hand.is_ryanpeiko(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='111122223333', man='22')
        self.assertTrue(hand.is_ryanpeiko(self._hand(tiles, 2)))

        tiles = self._string_to_34_array(sou='112233', man='123', pin='23444')
        self.assertFalse(hand.is_ryanpeiko(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='112233', man='33', pin='223344')
        win_tile = self._string_to_136_tile(pin='3')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 3)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=[[0, 1, 2]])
        self.assertNotEqual(result['error'], None)

    def test_is_sanshoku(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='123', man='123', pin='12345677')
        self.assertTrue(hand.is_sanshoku(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='123456', man='23455', pin='123')
        self.assertFalse(hand.is_sanshoku(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='123456', man='12399', pin='123')
        win_tile = self._string_to_136_tile(man='2')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=[[0, 1, 2]])
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_sanshoku_douko(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='111', man='111', pin='11145677')
        self.assertTrue(hand.is_sanshoku_douko(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='111', man='222', pin='33344455')
        self.assertFalse(hand.is_sanshoku_douko(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='222', man='222', pin='22245699')
        win_tile = self._string_to_136_tile(pin='9')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_toitoi(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='111333', man='333', pin='44555')
        self.assertTrue(hand.is_toitoi(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='111333', man='333', pin='44555')
        open_sets = [self._string_to_136_array(sou='111'), self._string_to_136_array(sou='333')]
        win_tile = self._string_to_136_tile(pin='5')

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=open_sets)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_sankantsu(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='111333', man='123', pin='44666')
        called_kan_indices = [self._string_to_34_tile(sou='1'), self._string_to_34_tile(sou='3'),
                              self._string_to_34_tile(pin='6')]
        self.assertTrue(hand.is_sankantsu(self._hand(tiles, 0), called_kan_indices))

        tiles = self._string_to_136_array(sou='111333', man='123', pin='44666')
        open_sets = [self._string_to_136_array(sou='111'), self._string_to_136_array(sou='333')]
        win_tile = self._string_to_136_tile(man='3')

        called_kan_indices = [self._string_to_136_tile(sou='1'), self._string_to_136_tile(sou='3'),
                              self._string_to_136_tile(pin='6')]

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=open_sets, called_kan_indices=called_kan_indices)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 70)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_honroto(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='111999', man='111', honors='11222')
        self.assertTrue(hand.is_honroto(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='111999', man='111', honors='11222')
        win_tile = self._string_to_136_tile(honors='2')
        open_sets = [self._string_to_136_array(sou='111')]

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=open_sets)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 4)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 2)

    def test_is_sanankou(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='111444', man='333', pin='44555')
        open_sets = [self._string_to_open_34_set(sou='444'), self._string_to_open_34_set(sou='111')]
        win_tile = self._string_to_136_tile(sou='4')

        self.assertFalse(hand.is_sanankou(win_tile, self._hand(tiles, 0), open_sets, False))

        open_sets = [self._string_to_open_34_set(sou='111')]
        self.assertFalse(hand.is_sanankou(win_tile, self._hand(tiles, 0), open_sets, False))
        self.assertTrue(hand.is_sanankou(win_tile, self._hand(tiles, 0), open_sets, True))

        tiles = self._string_to_136_array(sou='123444', man='333', pin='44555')
        open_sets = [self._string_to_136_array(sou='123')]
        win_tile = self._string_to_136_tile(pin='5')

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=open_sets, is_tsumo=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_shosangen(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='123', man='345', honors='55666777')
        self.assertTrue(hand.is_shosangen(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='123', man='345', honors='55666777')
        win_tile = self._string_to_136_tile(honors='7')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 4)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 3)

    def test_is_chanta(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='123', man='123789', honors='22333')
        self.assertTrue(hand.is_chanta(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='111', man='111999', honors='22333')
        self.assertFalse(hand.is_chanta(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='111999', man='111999', pin='11999')
        self.assertFalse(hand.is_chanta(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='123', man='123789', honors='22333')
        win_tile = self._string_to_136_tile(honors='3')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=[[0, 1, 2]])
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_junchan(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='789', man='123789', pin='12399')
        self.assertTrue(hand.is_junchan(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='111', man='111999', honors='22333')
        self.assertFalse(hand.is_junchan(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(sou='111999', man='111999', pin='11999')
        self.assertFalse(hand.is_junchan(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='789', man='123789', pin='12399')
        win_tile = self._string_to_136_tile(sou='8')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 3)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=[[0, 1, 2]])
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_honitsu(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(man='123456789', honors='11122')
        self.assertTrue(hand.is_honitsu(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(man='123456789', pin='123', honors='22')
        self.assertFalse(hand.is_honitsu(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(man='12345666778899')
        self.assertFalse(hand.is_honitsu(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(man='123455667', honors='11122')
        win_tile = self._string_to_136_tile(honors='2')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 3)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=[[0, 1, 2]])
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_chinitsu(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(man='12345666778899')
        self.assertTrue(hand.is_chinitsu(self._hand(tiles, 0)))

        tiles = self._string_to_34_array(man='123456778899', honors='22')
        self.assertFalse(hand.is_chinitsu(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(man='11234567677889')
        win_tile = self._string_to_136_tile(man='1')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 6)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=[[0, 1, 2]])
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 5)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_ittsu(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(man='123456789', sou='123', honors='22')
        self.assertTrue(hand.is_ittsu(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(man='123456789', sou='123', honors='22')
        win_tile = self._string_to_136_tile(sou='3')

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, open_sets=[[0, 1, 2]])
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_haku(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='234567', man='23422', honors='555')
        self.assertTrue(hand.is_haku(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='234567', man='23422', honors='555')
        win_tile = self._string_to_136_tile(honors='5')

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_hatsu(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='234567', man='23422', honors='666')
        self.assertTrue(hand.is_hatsu(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='234567', man='23422', honors='666')
        win_tile = self._string_to_136_tile(honors='6')

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_chun(self):
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='234567', man='23422', honors='777')
        self.assertTrue(hand.is_chun(self._hand(tiles, 0)))

        tiles = self._string_to_136_array(sou='234567', man='23422', honors='777')
        win_tile = self._string_to_136_tile(honors='7')

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_east(self):
        player_wind, round_wind = EAST, WEST
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='234567', man='23422', honors='111')
        self.assertTrue(hand.is_east(self._hand(tiles, 0), player_wind, round_wind))

        tiles = self._string_to_136_array(sou='234567', man='23422', honors='111')
        win_tile = self._string_to_136_tile(honors='1')

        result = hand.estimate_hand_value(tiles,
                                          win_tile,
                                          is_tsumo=False,
                                          is_riichi=False,
                                          player_wind=player_wind,
                                          round_wind=round_wind)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        round_wind = EAST
        result = hand.estimate_hand_value(tiles,
                                          win_tile,
                                          is_tsumo=False,
                                          is_riichi=False,
                                          player_wind=player_wind,
                                          round_wind=round_wind)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 2)

    def test_is_south(self):
        player_wind, round_wind = SOUTH, EAST
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='234567', man='23422', honors='222')
        self.assertTrue(hand.is_south(self._hand(tiles, 0), player_wind, round_wind))

        tiles = self._string_to_136_array(sou='234567', man='23422', honors='222')
        win_tile = self._string_to_136_tile(honors='2')

        result = hand.estimate_hand_value(tiles,
                                          win_tile,
                                          is_tsumo=False,
                                          is_riichi=False,
                                          player_wind=player_wind,
                                          round_wind=round_wind)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        round_wind = SOUTH
        result = hand.estimate_hand_value(tiles,
                                          win_tile,
                                          is_tsumo=False,
                                          is_riichi=False,
                                          player_wind=player_wind,
                                          round_wind=round_wind)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 2)

    def test_is_west(self):
        player_wind, round_wind = WEST, EAST
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='234567', man='23422', honors='333')
        self.assertTrue(hand.is_west(self._hand(tiles, 0), player_wind, round_wind))

        tiles = self._string_to_136_array(sou='234567', man='23422', honors='333')
        win_tile = self._string_to_136_tile(honors='3')

        result = hand.estimate_hand_value(tiles,
                                          win_tile,
                                          is_tsumo=False,
                                          is_riichi=False,
                                          player_wind=player_wind,
                                          round_wind=round_wind)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        round_wind = WEST
        result = hand.estimate_hand_value(tiles,
                                          win_tile,
                                          is_tsumo=False,
                                          is_riichi=False,
                                          player_wind=player_wind,
                                          round_wind=round_wind)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 2)

    def test_is_north(self):
        player_wind, round_wind = NORTH, EAST
        hand = FinishedHand()

        tiles = self._string_to_34_array(sou='234567', man='23422', honors='444')
        self.assertTrue(hand.is_north(self._hand(tiles, 0), player_wind, round_wind))

        tiles = self._string_to_136_array(sou='234567', man='23422', honors='444')
        win_tile = self._string_to_136_tile(honors='4')

        result = hand.estimate_hand_value(tiles,
                                          win_tile,
                                          is_tsumo=False,
                                          is_riichi=False,
                                          player_wind=player_wind,
                                          round_wind=round_wind)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        round_wind = NORTH
        result = hand.estimate_hand_value(tiles,
                                          win_tile,
                                          is_tsumo=False,
                                          is_riichi=False,
                                          player_wind=player_wind,
                                          round_wind=round_wind)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 2)

    def test_dora_in_hand(self):
        hand = FinishedHand()

        tiles = self._string_to_136_array(sou='123456', man='123456', pin='33')
        win_tile = self._string_to_136_tile(man='6')

        dora_indicators = [self._string_to_136_tile(pin='2')]
        result = hand.estimate_hand_value(tiles, win_tile, dora_indicators=dora_indicators)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 3)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 2)

        tiles = self._string_to_136_array(man='22456678', pin='123678')
        win_tile = self._string_to_136_tile(man='2')
        dora_indicators = [self._string_to_136_tile(man='1'), self._string_to_136_tile(pin='2')]
        result = hand.estimate_hand_value(tiles, win_tile, dora_indicators=dora_indicators)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 3)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        # double dora
        tiles = self._string_to_136_array(man='678', pin='34577', sou='123345')
        win_tile = self._string_to_136_tile(pin='7')
        dora_indicators = [self._string_to_136_tile(sou='4'), self._string_to_136_tile(sou='4')]
        result = hand.estimate_hand_value(tiles, win_tile, dora_indicators=dora_indicators)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        settings.FIVE_REDS = True

        # double dora indicators and red fives
        tiles = self._string_to_136_array(sou='12346', man='123678', pin='44')
        win_tile = self._string_to_136_tile(pin='4')
        tiles.append(FIVE_RED_SOU)
        dora_indicators = [self._string_to_136_tile(pin='2'), self._string_to_136_tile(pin='2')]
        result = hand.estimate_hand_value(tiles, win_tile, dora_indicators=dora_indicators)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        settings.FIVE_REDS = False

        # dora in kan
        tiles = self._string_to_136_array(man='777', pin='34577', sou='123345')
        win_tile = self._string_to_136_tile(pin='7')
        dora_indicators = [self._string_to_136_tile(man='6')]
        called_kan_indices = [self._string_to_136_tile(man='7')]
        result = hand.estimate_hand_value(tiles, win_tile, dora_indicators=dora_indicators,
                                          called_kan_indices=called_kan_indices)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 4)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 1)

        # we had a bug with multiple dora indicators and honor sets
        # this test is working with this situation
        tiles = self._string_to_136_array(pin='22244456799', honors='444')
        win_tile = self._string_to_136_tile(pin='2')
        dora_indicators = [self._string_to_136_tile(sou='3'), self._string_to_136_tile(honors='3')]
        called_kan_indices = [self._string_to_136_tile(honors='4')]
        result = hand.estimate_hand_value(tiles, win_tile, dora_indicators=dora_indicators,
                                          called_kan_indices=called_kan_indices)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 7)
        self.assertEqual(result['fu'], 70)
        self.assertEqual(len(result['hand_yaku']), 2)

        # one more bug with with dora tiles
        tiles = self._string_to_136_array(sou='123456789', honors='11555')
        win_tile = self._string_to_136_tile(sou='9')
        open_sets = [self._string_to_136_array(sou='456'), self._string_to_136_array(sou='555')]
        dora_indicators = [self._string_to_136_tile(sou='9')]
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True, open_sets=open_sets,
                                          dora_indicators=dora_indicators)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(result['han'], 5)
