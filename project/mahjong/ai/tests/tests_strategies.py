# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.shanten import Shanten
from mahjong.ai.strategies.honitsu import HonitsuStrategy
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.ai.strategies.tanyao import TanyaoStrategy
from mahjong.ai.strategies.yakuhai import YakuhaiStrategy
from mahjong.meld import Meld
from mahjong.player import Player
from mahjong.table import Table
from utils.tests import TestMixin


class YakuhaiStrategyTestCase(unittest.TestCase, TestMixin):

    def test_should_activate_strategy(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)

        tiles = self._string_to_136_array(sou='12355689', man='89', honors='123')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='12355689', man='89', honors='44')
        player.init_hand(tiles)
        player.dealer_seat = 1
        self.assertEqual(strategy.should_activate_strategy(), True)

        tiles = self._string_to_136_array(sou='12355689', man='89', honors='666')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

        # with chitoitsu-like hand we don't need to go for yakuhai
        tiles = self._string_to_136_array(sou='1235566', man='8899', honors='66')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

    def test_dont_activate_strategy_if_we_dont_have_enough_tiles_in_the_wall(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)

        tiles = self._string_to_136_array(sou='12355689', man='89', honors='44')
        player.init_hand(tiles)
        player.dealer_seat = 1
        self.assertEqual(strategy.should_activate_strategy(), True)

        table.enemy_discard(self._string_to_136_tile(honors='4'), 3)
        table.enemy_discard(self._string_to_136_tile(honors='4'), 3)

        # we can't complete yakuhai, because there is not enough honor tiles
        self.assertEqual(strategy.should_activate_strategy(), False)

    def test_suitable_tiles(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)

        # for yakuhai we can use any tile
        for tile in range(0, 136):
            self.assertEqual(strategy.is_tile_suitable(tile), True)

    def test_open_hand_with_yakuhai_pair_in_hand(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(sou='123678', pin='25899', honors='44')
        tile = self._string_to_136_tile(honors='4')
        player.init_hand(tiles)

        # we don't need to open hand with not our wind
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # with dragon pair in hand let's open our hand
        tiles = self._string_to_136_array(sou='1689', pin='2358', man='1', honors='4455')
        tile = self._string_to_136_tile(honors='4')
        player.init_hand(tiles)
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)
        player.add_called_meld(meld)
        player.tiles.append(tile)

        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(self._to_string(meld.tiles), '444z')
        self.assertEqual(len(player.closed_hand), 11)
        self.assertEqual(len(player.tiles), 14)
        player.discard_tile()

        tile = self._string_to_136_tile(honors='5')
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)
        player.add_called_meld(meld)
        player.tiles.append(tile)

        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(self._to_string(meld.tiles), '555z')
        self.assertEqual(len(player.closed_hand), 8)
        self.assertEqual(len(player.tiles), 14)
        player.discard_tile()

        tile = self._string_to_136_tile(sou='7')
        # we can call chi only from left player
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        meld, _, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        player.add_called_meld(meld)
        player.tiles.append(tile)

        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '678s')
        self.assertEqual(len(player.closed_hand), 5)
        self.assertEqual(len(player.tiles), 14)

    def test_force_yakuhai_pair_waiting_for_tempai_hand(self):
        """
        If hand shanten = 1 don't open hand except the situation where is
        we have tempai on yakuhai tile after open set
        """
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(sou='123', pin='678', man='34468', honors='66')
        tile = self._string_to_136_tile(man='5')
        player.init_hand(tiles)

        # we will not get tempai on yakuhai pair with this hand, so let's skip this call
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        tile = self._string_to_136_tile(man='7')
        meld, tile_to_discard, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '678m')

        # we can open hand in that case
        tiles = self._string_to_136_array(man='44556', sou='366789', honors='77')
        tile = self._string_to_136_tile(honors='7')
        player.init_hand(tiles)
        meld, tile_to_discard, shanten = player.try_to_call_meld(tile, True)
        self.assertEqual(self._to_string(meld.tiles), '777z')

    def test_call_yakuhai_pair_and_special_conditions(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='56', sou='1235', pin='12888', honors='11')
        player.init_hand(tiles)

        meld = self._make_meld(Meld.PON, self._string_to_136_array(pin='888'))
        player.add_called_meld(meld)

        # to update previous_shanten attribute
        player.draw_tile(self._string_to_136_tile(honors='3'))
        player.discard_tile()

        tile = self._string_to_136_tile(honors='1')
        meld, tile_to_discard, shanten = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='56', sou='1235', pin='12', honors='11777')
        player.init_hand(tiles)

        meld = self._make_meld(Meld.PON, self._string_to_136_array(honors='777'))
        player.add_called_meld(meld)
        # to update previous_shanten attribute
        player.draw_tile(self._string_to_136_tile(honors='3'))
        player.discard_tile()

        # we don't need to open hand with already opened yakuhai set
        tile = self._string_to_136_tile(honors='1')
        meld, tile_to_discard, shanten = player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

    def test_tempai_without_yaku(self):
        table = Table()
        player = Player(0, 0, table)

        # 456m12355p22z + 5p [678s]
        tiles = self._string_to_136_array(sou='678', pin='12355', man='456', honors='77')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(pin='5')
        player.draw_tile(tile)
        meld = self._make_meld(Meld.CHI, self._string_to_136_array(sou='678'))
        player.add_called_meld(meld)

        discard = player.discard_tile()
        self.assertEqual(self._to_string([discard]), '5p')


class HonitsuStrategyTestCase(unittest.TestCase, TestMixin):

    def test_should_activate_strategy(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)

        tiles = self._string_to_136_array(sou='12355', man='12389', honors='123')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='12355', man='238', honors='11234')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

        # with hand without pairs we not should go for honitsu,
        # because it is far away from tempai
        tiles = self._string_to_136_array(sou='12358', man='238', honors='12345')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        # with chitoitsu-like hand we don't need to go for honitsu
        tiles = self._string_to_136_array(pin='77', man='3355677899', sou='11')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

    def test_suitable_tiles(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)

        tiles = self._string_to_136_array(sou='12355', man='238', honors='11234')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

        tile = self._string_to_136_tile(man='1')
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(pin='1')
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(strategy.is_tile_suitable(tile), True)

        tile = self._string_to_136_tile(honors='1')
        self.assertEqual(strategy.is_tile_suitable(tile), True)

    def test_open_hand_and_discard_tiles_logic(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(sou='112235589', man='23', honors='22')
        player.init_hand(tiles)

        # we don't need to call meld even if it improves our hand,
        # because we are collecting honitsu
        tile = self._string_to_136_tile(man='1')
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # any honor tile is suitable
        tile = self._string_to_136_tile(honors='2')
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)

        tile = self._string_to_136_tile(man='1')
        player.draw_tile(tile)
        tile_to_discard = player.discard_tile()

        # we are in honitsu mode, so we should discard man suits
        self.assertEqual(self._to_string([tile_to_discard]), '1m')

    def test_riichi_and_tiles_from_another_suit_in_the_hand(self):
        table = Table()
        player = Player(0, 0, table)
        player.scores = 25000
        table.count_of_remaining_tiles = 100

        tiles = self._string_to_136_array(man='3335689', pin='456', honors='155')
        player.init_hand(tiles)

        player.draw_tile(self._string_to_136_tile(man='4'))
        tile_to_discard = player.discard_tile()

        # we don't need to go for honitsu here
        # we already in tempai
        self.assertEqual(self._to_string([tile_to_discard]), '1z')


class TanyaoStrategyTestCase(unittest.TestCase, TestMixin):

    def test_should_activate_strategy_and_terminal_pon_sets(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='233', honors='111')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='233999')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='233444')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_should_activate_strategy_and_terminal_pairs(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='2399', honors='11')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='345669', pin='2399')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_should_activate_strategy_and_valued_pair(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        tiles = self._string_to_136_array(man='23446679', sou='345', honors='55')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(man='23446679', sou='345', honors='22')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_should_activate_strategy_and_chitoitsu_like_hand(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        tiles = self._string_to_136_array(sou='223388', man='3344', pin='6687')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

    def test_should_activate_strategy_and_already_completed_sided_set(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        tiles = self._string_to_136_array(sou='123234', man='3459', pin='234')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234789', man='3459', pin='234')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='1233459', pin='234')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3457899', pin='234')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='122334')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='234789')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='223344', man='3459', pin='234')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_suitable_tiles(self):
        table = Table()
        player = Player(0, 0, table)
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        tile = self._string_to_136_tile(man='1')
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(pin='1')
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(sou='9')
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(honors='1')
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(honors='6')
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(man='2')
        self.assertEqual(strategy.is_tile_suitable(tile), True)

        tile = self._string_to_136_tile(pin='5')
        self.assertEqual(strategy.is_tile_suitable(tile), True)

        tile = self._string_to_136_tile(sou='8')
        self.assertEqual(strategy.is_tile_suitable(tile), True)

    def test_dont_open_hand_with_high_shanten(self):
        table = Table()
        player = Player(0, 0, table)

        # with 4 shanten we don't need to aim for open tanyao
        tiles = self._string_to_136_array(man='369', pin='378', sou='3488', honors='123')
        tile = self._string_to_136_tile(sou='2')
        player.init_hand(tiles)
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # with 3 shanten we can open a hand
        tiles = self._string_to_136_array(man='236', pin='378', sou='3488', honors='123')
        tile = self._string_to_136_tile(sou='2')
        player.init_hand(tiles)
        meld, _, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

    def test_dont_open_hand_with_not_suitable_melds(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='33355788', sou='3479', honors='3')
        tile = self._string_to_136_tile(sou='8')
        player.init_hand(tiles)
        meld, _, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_open_hand_and_discard_tiles_logic(self):
        table = Table()
        player = Player(0, 0, table)

        # 2345779m1p256s44z
        tiles = self._string_to_136_array(man='22345777', sou='238', honors='44')
        player.init_hand(tiles)

        # if we are in tanyao
        # we need to discard terminals and honors
        tile = self._string_to_136_tile(sou='4')
        meld, tile_to_discard, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string([tile_to_discard]), '4z')

        tile = self._string_to_136_tile(pin='5')
        player.draw_tile(tile)
        tile_to_discard = player.discard_tile()

        # we are in tanyao, so we should discard honors and terminals
        self.assertEqual(self._to_string([tile_to_discard]), '4z')

    def test_dont_count_pairs_in_already_opened_hand(self):
        table = Table()
        player = Player(0, 0, table)

        meld = self._make_meld(Meld.PON, self._string_to_136_array(sou='222'))
        player.add_called_meld(meld)

        tiles = self._string_to_136_array(man='33556788', sou='22266')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='6')
        meld, _, _ = player.try_to_call_meld(tile, False)
        # even if it looks like chitoitsu we can open hand and get tempai here
        self.assertNotEqual(meld, None)

    def test_we_cant_win_with_this_hand(self):
        table = Table()
        player = Player(0, 0, table)

        tiles = self._string_to_136_array(man='34577', sou='23', pin='233445')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(sou='1'))
        player.ai.current_strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)
        # print(player.ai.current_strategy)

        discard = player.discard_tile()
        # hand was closed and we have won!
        self.assertEqual(discard, Shanten.AGARI_STATE)

        meld = self._make_meld(Meld.CHI, self._string_to_136_array(pin='234'))
        player.add_called_meld(meld)

        discard = player.discard_tile()
        # but for already open hand we cant do tsumo
        # because we don't have a yaku here
        self.assertEqual(self._to_string([discard]), '1s')
