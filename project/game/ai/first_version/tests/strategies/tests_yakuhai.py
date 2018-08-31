# -*- coding: utf-8 -*-
import unittest

from mahjong.constants import WEST, EAST, SOUTH
from mahjong.meld import Meld
from mahjong.tests_mixin import TestMixin
from mahjong.tile import Tile

from game.ai.first_version.strategies.main import BaseStrategy
from game.ai.first_version.strategies.yakuhai import YakuhaiStrategy
from game.table import Table


class YakuhaiStrategyTestCase(unittest.TestCase, TestMixin):

    def setUp(self):
        self.table = Table()
        self.player = self.table.player
        self.player.dealer_seat = 3

    def test_should_activate_strategy(self):
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, self.player)

        tiles = self._string_to_136_array(sou='12355689', man='89', honors='123')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        self.table.dora_indicators.append(self._string_to_136_tile(honors='7'))
        tiles = self._string_to_136_array(sou='12355689', man='899', honors='55')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), True)

        # with chitoitsu-like hand we don't need to go for yakuhai
        tiles = self._string_to_136_array(sou='1235566', man='8899', honors='66')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

    def test_dont_activate_strategy_if_we_dont_have_enough_tiles_in_the_wall(self):
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, self.player)

        self.table.dora_indicators.append(self._string_to_136_tile(honors='7'))
        tiles = self._string_to_136_array(man='59', sou='1235', pin='12789', honors='55')
        self.player.init_hand(tiles)

        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), True)

        self.table.add_discarded_tile(3, self._string_to_136_tile(honors='5'), False)
        self.table.add_discarded_tile(3, self._string_to_136_tile(honors='5'), False)

        # we can't complete yakuhai, because there is not enough honor tiles
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

    def test_suitable_tiles(self):
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, self.player)

        # for yakuhai we can use any tile
        for tile in range(0, 136):
            self.assertEqual(strategy.is_tile_suitable(tile), True)

    def test_force_yakuhai_pair_waiting_for_tempai_hand(self):
        """
        If hand shanten = 1 don't open hand except the situation where is
        we have tempai on yakuhai tile after open set
        """
        self.table.dora_indicators.append(self._string_to_136_tile(man='3'))
        tiles = self._string_to_136_array(sou='123', pin='678', man='34468', honors='66')
        self.player.init_hand(tiles)

        # we will not get tempai on yakuhai pair with this hand, so let's skip this call
        tile = self._string_to_136_tile(man='5')
        meld, _ = self.player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # but here we will have atodzuke tempai
        tile = self._string_to_136_tile(man='7')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '678m')

        self.table = Table()
        self.player = self.table.player

        # we can open hand in that case
        self.table.dora_indicators.append(self._string_to_136_tile(sou='5'))
        tiles = self._string_to_136_array(man='44556', sou='366789', honors='77')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='7')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string(meld.tiles), '777z')

    def test_tempai_without_yaku(self):
        tiles = self._string_to_136_array(sou='678', pin='12355', man='456', honors='77')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(pin='5')
        self.player.draw_tile(tile)
        meld = self._make_meld(Meld.CHI, sou='678')
        self.player.add_called_meld(meld)

        discard = self.player.discard_tile()
        self.assertEqual(self._to_string([discard]), '1p')

    def test_wrong_shanten_improvements_detection(self):
        """
        With hand 2345s1p11z bot wanted to open set on 2s,
        so after opened set we will get 25s1p11z
        it is not correct logic, because we ruined our hand
        :return:
        """
        tiles = self._string_to_136_array(sou='2345999', honors='114446')
        self.player.init_hand(tiles)

        meld = self._make_meld(Meld.PON, sou='999')
        self.player.add_called_meld(meld)
        meld = self._make_meld(Meld.PON, honors='444')
        self.player.add_called_meld(meld)

        tile = self._string_to_136_tile(sou='2')
        meld, _ = self.table.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

    def test_open_hand_with_doras_in_the_hand(self):
        """
        If we have valuable pair in the hand, and 2+ dora let's open on this
        valuable pair
        """

        tiles = self._string_to_136_array(man='59', sou='1235', pin='12789', honors='11')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='1')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

        # add doras to the hand
        self.table.dora_indicators.append(self._string_to_136_tile(pin='7'))
        self.table.dora_indicators.append(self._string_to_136_tile(pin='8'))
        self.player.init_hand(tiles)

        # and now we can open hand on the valuable pair
        tile = self._string_to_136_tile(honors='1')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

        # but we don't need to open hand for atodzuke here
        tile = self._string_to_136_tile(pin='3')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

    def test_open_hand_with_doras_in_the_hand_and_atodzuke(self):
        """
        If we have valuable pair in the hand, and 2+ dora we can open hand on any tile
        but only if we have other pair in the hand
        """

        tiles = self._string_to_136_array(man='59', sou='1235', pin='12788', honors='11')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(pin='3')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

        # add doras to the hand
        self.table.dora_indicators.append(self._string_to_136_tile(pin='7'))
        self.player.init_hand(tiles)

        # we have other pair in the hand, so we can open atodzuke here
        tile = self._string_to_136_tile(pin='3')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

    def test_open_hand_on_fifth_round_step(self):
        """
        If we have valuable pair in the hand, 1+ dora and 5+ round step
        let's open on this valuable pair
        """

        tiles = self._string_to_136_array(man='59', sou='1235', pin='12789', honors='11')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='1')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

        # add doras to the hand
        self.table.dora_indicators.append(self._string_to_136_tile(pin='7'))
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='1')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

        # one discard == one round step
        self.player.add_discarded_tile(Tile(0, False))
        self.player.add_discarded_tile(Tile(0, False))
        self.player.add_discarded_tile(Tile(0, False))
        self.player.add_discarded_tile(Tile(0, False))
        self.player.add_discarded_tile(Tile(0, False))
        self.player.add_discarded_tile(Tile(0, False))
        self.player.init_hand(tiles)

        # after 5 round step we can open hand
        tile = self._string_to_136_tile(honors='1')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

        # but we don't need to open hand for atodzuke here
        tile = self._string_to_136_tile(pin='3')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

    def test_open_hand_with_two_valuable_pairs(self):
        """
        If we have two valuable pairs in the hand and 1+ dora
        let's open on one of this valuable pairs
        """

        tiles = self._string_to_136_array(man='59', sou='12', pin='12789', honors='5566')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='5')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

        # add doras to the hand
        self.table.dora_indicators.append(self._string_to_136_tile(pin='7'))
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='5')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

        tile = self._string_to_136_tile(honors='6')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

        # but we don't need to open hand for atodzuke here
        tile = self._string_to_136_tile(pin='3')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

    def test_open_hand_and_once_discarded_tile(self):
        """
        If we have valuable pair in the hand, this tile was discarded once and we have 1+ shanten
        let's open on this valuable pair
        """

        tiles = self._string_to_136_array(man='29', sou='1189', pin='12789', honors='11')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(man='6'))

        tile = self._string_to_136_tile(honors='1')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

        self.table.add_discarded_tile(1, self._string_to_136_tile(honors='1'), False)
        tiles = self._string_to_136_array(man='29', sou='1189', pin='12789', honors='11')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='1')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

        # but we don't need to open hand for atodzuke here
        tile = self._string_to_136_tile(pin='3')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

    def test_open_hand_when_yakuhai_already_in_the_hand(self):
        tiles = self._string_to_136_array(man='46', pin='4679', sou='1348', honors='555')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='2')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

    def test_always_open_double_east_wind(self):
        tiles = self._string_to_136_array(man='59', sou='1235', pin='12788', honors='11')
        self.player.init_hand(tiles)

        # player is is not east
        self.player.dealer_seat = 2
        self.assertEqual(self.player.player_wind, WEST)

        self.player.init_hand(tiles)
        tile = self._string_to_136_tile(honors='1')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

        # player is is east
        self.player.dealer_seat = 0
        self.assertEqual(self.player.player_wind, EAST)

        self.player.init_hand(tiles)
        tile = self._string_to_136_tile(honors='1')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

    def test_open_double_south_wind(self):
        tiles = self._string_to_136_array(man='59', sou='1235', pin='12788', honors='22')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='2')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

        # player is south and round is south
        self.table.round_number = 5
        self.player.dealer_seat = 3
        self.assertEqual(self.player.player_wind, SOUTH)

        self.player.init_hand(tiles)
        tile = self._string_to_136_tile(honors='2')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

        # add dora in the hand and after that we can open a hand
        self.table.dora_indicators.append(self._string_to_136_tile(pin='6'))

        self.player.init_hand(tiles)
        tile = self._string_to_136_tile(honors='2')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
