# -*- coding: utf-8 -*-
import unittest

from mahjong.hand import FinishedHand, HandDivider
from mahjong.tile import TilesConverter
from mahjong.constants import EAST, SOUTH, WEST, NORTH


class YakuCalculationTestCase(unittest.TestCase):

    def test_hand_dividing(self):
        hand = HandDivider()

        tiles_34 = TilesConverter.string_to_34_array(sou='234567', man='23455', honors='777')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [[1, 2, 3], [4, 5, 6], [19, 20, 21], [22, 22], [33, 33, 33]])

        tiles_34 = TilesConverter.string_to_34_array(sou='123', pin='123', man='123', honors='11222')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [[0, 1, 2], [9, 10, 11], [18, 19, 20], [27, 27], [28, 28, 28]])

        tiles_34 = TilesConverter.string_to_34_array(sou='23444', pin='344556', man='333')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [[1, 2, 3], [3, 3], [11, 12, 13], [12, 13, 14], [20, 20, 20]])

        tiles_34 = TilesConverter.string_to_34_array(sou='11122233388899')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [[0, 1, 2], [0, 1, 2], [0, 1, 2], [7, 7, 7], [8, 8]])
        self.assertEqual(result[1], [[0, 0, 0], [1, 1, 1], [2, 2, 2], [7, 7, 7], [8, 8]])

        tiles_34 = TilesConverter.string_to_34_array(sou='112233', man='445566', pin='99')
        result = hand.divide_hand(tiles_34)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [[0, 1, 2], [0, 1, 2], [17, 17], [21, 22, 23], [21, 22, 23]])
        self.assertEqual(result[1], [[0, 0], [1, 1], [2, 2], [17, 17], [21, 21], [22, 22], [23, 23]])

    def test_fu_calculation(self):
        hand = FinishedHand()
        hand_divider = HandDivider()
        player_wind, round_wind = EAST, WEST

        tiles = TilesConverter.string_to_136_array(sou='12378', man='123456', pin='22')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False)
        self.assertEqual(result['fu'], 30)
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True)
        self.assertEqual(result['fu'], 20)

        # penchan waiting
        tiles = TilesConverter.string_to_136_array(sou='12456', man='123456', pin='55')
        win_tile = TilesConverter.string_to_136_array(sou='3')[0]
        hand_tiles = hand_divider.divide_hand(TilesConverter.to_34_array(tiles + [win_tile]))
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles[0], player_wind, round_wind))

        # kanchan waiting
        tiles = TilesConverter.string_to_136_array(sou='12357', man='123456', pin='55')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]
        hand_tiles = hand_divider.divide_hand(TilesConverter.to_34_array(tiles + [win_tile]))
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles[0], player_wind, round_wind))

        # valued pair
        tiles = TilesConverter.string_to_136_array(sou='12378', man='123456', honors='11')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]
        hand_tiles = hand_divider.divide_hand(TilesConverter.to_34_array(tiles + [win_tile]))
        self.assertEqual(2, hand.calculate_additional_fu(win_tile, hand_tiles[0], player_wind, round_wind))

        # pon
        tiles = TilesConverter.string_to_136_array(sou='22278', man='123456', pin='11')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]
        hand_tiles = hand_divider.divide_hand(TilesConverter.to_34_array(tiles + [win_tile]))
        self.assertEqual(4, hand.calculate_additional_fu(win_tile, hand_tiles[0], player_wind, round_wind))

        # terminal pon
        tiles = TilesConverter.string_to_136_array(sou='11178', man='123456', pin='11')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]
        hand_tiles = hand_divider.divide_hand(TilesConverter.to_34_array(tiles + [win_tile]))
        self.assertEqual(8, hand.calculate_additional_fu(win_tile, hand_tiles[0], player_wind, round_wind))

        # honor pon
        tiles = TilesConverter.string_to_136_array(sou='78', man='123456', pin='11', honors='111')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]
        hand_tiles = hand_divider.divide_hand(TilesConverter.to_34_array(tiles + [win_tile]))
        self.assertEqual(8, hand.calculate_additional_fu(win_tile, hand_tiles[0], player_wind, round_wind))

    def test_is_riichi(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_riichi=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, is_riichi=True, is_open_hand=True)
        self.assertNotEqual(result['error'], None)

    def test_is_tsumo(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True, is_open_hand=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

        # with open hand tsumo not giving yaku
        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=True, is_open_hand=True)
        self.assertNotEqual(result['error'], None)

    def test_is_ippatsu(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

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

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_rinshan=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_chankan(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_chankan=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_haitei(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_haitei=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_houtei(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_houtei=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_daburu_riichi(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='12344', man='234456', pin='66')
        win_tile = TilesConverter.string_to_136_array(sou='4')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_daburu_riichi=True, is_riichi=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_nagashi_mangan(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='13579', man='234456', pin='66')

        result = hand.estimate_hand_value(tiles, None, is_nagashi_mangan=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 5)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

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
        self.assertEqual(len(result['hand_yaku']), 3)

    def test_is_pinfu_hand(self):
        player_wind, round_wind = EAST, WEST
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='123456', man='12345', pin='55')
        win_tile = TilesConverter.string_to_136_array(man='6')[0]
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

        # waiting in two pairs
        tiles = TilesConverter.string_to_136_array(sou='123456', man='12355', pin='55')
        win_tile = TilesConverter.string_to_136_array(man='5')[0]
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertNotEqual(result['error'], None)

        # contains pon or kan
        tiles = TilesConverter.string_to_136_array(sou='111456', man='12345', pin='55')
        win_tile = TilesConverter.string_to_136_array(man='6')[0]
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertNotEqual(result['error'], None)

        # penchan waiting
        tiles = TilesConverter.string_to_136_array(sou='12456', man='123456', pin='55')
        win_tile = TilesConverter.string_to_136_array(sou='3')[0]
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertNotEqual(result['error'], None)

        # kanchan waiting
        tiles = TilesConverter.string_to_136_array(sou='12357', man='123456', pin='55')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertNotEqual(result['error'], None)

        # valued pair
        tiles = TilesConverter.string_to_136_array(sou='12378', man='123456', honors='11')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]
        result = hand.estimate_hand_value(tiles, win_tile, player_wind=player_wind, round_wind=round_wind)
        self.assertNotEqual(result['error'], None)

        # not valued pair
        tiles = TilesConverter.string_to_136_array(sou='12378', man='123456', honors='22')
        win_tile = TilesConverter.string_to_136_array(sou='6')[0]
        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_iipeiko(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='112233', man='123', pin='23444')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_iipeiko(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(sou='112233', man='33', pin='12344')
        win_tile = TilesConverter.string_to_136_array(man='3')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_open_hand=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, is_open_hand=True)
        self.assertNotEqual(result['error'], None)

    def test_is_toitoi(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='111333', man='333', pin='44555')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_toitoi(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(sou='111333', man='333', pin='4455')
        win_tile = TilesConverter.string_to_136_array(pin='5')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_shosangen(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='123', man='345', honors='55666777')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_shosangen(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(sou='123', man='345', honors='5566677')
        win_tile = TilesConverter.string_to_136_array(honors='7')[0]

        result = hand.estimate_hand_value(tiles, win_tile)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 4)
        self.assertEqual(result['fu'], 50)
        self.assertEqual(len(result['hand_yaku']), 3)

    def test_is_chanta(self):
        hand_divider = HandDivider()
        hand = FinishedHand()

        tiles = TilesConverter.string_to_34_array(sou='123', man='123789', honors='22333')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertTrue(hand.is_chanta(hand_tiles[0]))

        tiles = TilesConverter.string_to_34_array(sou='111', man='111999', honors='22333')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertFalse(hand.is_chanta(hand_tiles[0]))

        tiles = TilesConverter.string_to_34_array(sou='111999', man='111999', pin='11999')
        hand_tiles = hand_divider.divide_hand(tiles)
        self.assertFalse(hand.is_chanta(hand_tiles[0]))

        tiles = TilesConverter.string_to_136_array(sou='123', man='123789', honors='2233')
        win_tile = TilesConverter.string_to_136_array(honors='3')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_open_hand=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 2)
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

        result = hand.estimate_hand_value(tiles, win_tile, is_open_hand=True)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 30)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_haku(self):
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='555')
        self.assertTrue(hand.is_haku(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='55')
        win_tile = TilesConverter.string_to_136_array(honors='5')[0]

        result = hand.estimate_hand_value(tiles, win_tile, is_tsumo=False, is_riichi=False)
        self.assertEqual(result['error'], None)
        self.assertEqual(result['han'], 1)
        self.assertEqual(result['fu'], 40)
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
        self.assertEqual(result['fu'], 40)
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
        self.assertEqual(result['fu'], 40)
        self.assertEqual(len(result['hand_yaku']), 1)

    def test_is_east(self):
        player_wind, round_wind = EAST, WEST
        hand = FinishedHand()

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='111')
        tiles_34 = TilesConverter.to_34_array(tiles)
        self.assertTrue(hand.is_east(tiles_34, player_wind, round_wind))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='11')
        win_tile = TilesConverter.string_to_136_array(honors='1')[0]

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

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='222')
        tiles_34 = TilesConverter.to_34_array(tiles)
        self.assertTrue(hand.is_south(tiles_34, player_wind, round_wind))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='22')
        win_tile = TilesConverter.string_to_136_array(honors='2')[0]

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

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='333')
        tiles_34 = TilesConverter.to_34_array(tiles)
        self.assertTrue(hand.is_west(tiles_34, player_wind, round_wind))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='33')
        win_tile = TilesConverter.string_to_136_array(honors='3')[0]

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

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='444')
        tiles_34 = TilesConverter.to_34_array(tiles)
        self.assertTrue(hand.is_north(tiles_34, player_wind, round_wind))

        tiles = TilesConverter.string_to_136_array(sou='234567', man='23422', honors='44')
        win_tile = TilesConverter.string_to_136_array(honors='4')[0]

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
