# -*- coding: utf-8 -*-
import unittest

from mahjong.meld import Meld
from mahjong.tests_mixin import TestMixin

from game.ai.first_version.strategies.honitsu import HonitsuStrategy
from game.ai.first_version.strategies.main import BaseStrategy
from game.ai.first_version.strategies.tanyao import TanyaoStrategy
from game.ai.first_version.strategies.yakuhai import YakuhaiStrategy
from game.table import Table


class YakuhaiStrategyTestCase(unittest.TestCase, TestMixin):

    def test_should_activate_strategy(self):
        table = Table()
        player = table.player
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
        player = table.player
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)

        tiles = self._string_to_136_array(sou='12355689', man='89', honors='44')
        player.init_hand(tiles)
        player.dealer_seat = 1
        self.assertEqual(strategy.should_activate_strategy(), True)

        table.add_discarded_tile(3, self._string_to_136_tile(honors='4'), False)
        table.add_discarded_tile(3, self._string_to_136_tile(honors='4'), False)

        # we can't complete yakuhai, because there is not enough honor tiles
        self.assertEqual(strategy.should_activate_strategy(), False)

    def test_suitable_tiles(self):
        table = Table()
        player = table.player
        strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)

        # for yakuhai we can use any tile
        for tile in range(0, 136):
            self.assertEqual(strategy.is_tile_suitable(tile), True)

    def test_open_hand_with_yakuhai_pair_in_hand(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou='123678', pin='25899', honors='44')
        tile = self._string_to_136_tile(honors='4')
        player.init_hand(tiles)

        # we don't need to open hand with not our wind
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # with dragon pair in hand let's open our hand
        tiles = self._string_to_136_array(sou='1689', pin='2358', man='1', honors='4455')
        tile = self._string_to_136_tile(honors='4')
        player.init_hand(tiles)
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)
        player.add_called_meld(meld)
        player.tiles.append(tile)

        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(self._to_string(meld.tiles), '444z')
        self.assertEqual(len(player.closed_hand), 11)
        self.assertEqual(len(player.tiles), 14)
        player.discard_tile()

        tile = self._string_to_136_tile(honors='5')
        meld, _ = player.try_to_call_meld(tile, False)
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
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        meld, _ = player.try_to_call_meld(tile, True)
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
        player = table.player

        tiles = self._string_to_136_array(sou='123', pin='678', man='34468', honors='66')
        player.init_hand(tiles)

        # we will not get tempai on yakuhai pair with this hand, so let's skip this call
        tile = self._string_to_136_tile(man='5')
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # but here we will have atodzuke tempai
        tile = self._string_to_136_tile(man='7')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '678m')

        table = Table()
        player = table.player

        # we can open hand in that case
        tiles = self._string_to_136_array(man='44556', sou='366789', honors='77')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='7')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string(meld.tiles), '777z')

    def test_call_yakuhai_pair_and_special_conditions(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='56', sou='1235', pin='12888', honors='11')
        player.init_hand(tiles)

        meld = self._make_meld(Meld.PON, pin='888')
        player.add_called_meld(meld)

        # to update previous_shanten attribute
        player.draw_tile(self._string_to_136_tile(honors='3'))
        player.discard_tile()

        tile = self._string_to_136_tile(honors='1')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

    def test_tempai_without_yaku(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou='678', pin='12355', man='456', honors='77')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(pin='5')
        player.draw_tile(tile)
        meld = self._make_meld(Meld.CHI, sou='678')
        player.add_called_meld(meld)

        discard = player.discard_tile()
        self.assertEqual(self._to_string([discard]), '1p')

    def test_get_more_yakuhai_sets_in_hand(self):
        table = Table()

        tiles = self._string_to_136_array(sou='1378', pin='67', man='68', honors='5566')
        table.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='5')
        meld, discard_option = table.player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)

        table.add_called_meld(0, meld)
        table.player.tiles.append(tile)
        table.player.discard_tile(discard_option)

        tile = self._string_to_136_tile(honors='6')
        meld, _ = table.player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)

        table = Table()

        tiles = self._string_to_136_array(sou='234', pin='788', man='567', honors='5566')
        table.player.init_hand(tiles)

        tile = self._string_to_136_tile(honors='5')
        meld, discard_option = table.player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)

        table.add_called_meld(0, meld)
        table.player.tiles.append(tile)
        table.player.discard_tile(discard_option)

        tile = self._string_to_136_tile(honors='6')
        meld, _ = table.player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_atodzuke_opened_hand(self):
        table = Table()
        player = table.player

        # 456m12355p22z + 5p [678s]
        tiles = self._string_to_136_array(sou='4589', pin='123', man='1236', honors='66')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(man='6')
        player.draw_tile(tile)
        meld = self._make_meld(Meld.CHI, pin='123')
        player.add_called_meld(meld)

        discard = player.discard_tile()
        self.assertEqual(self._to_string([discard]), '9s')

    def test_wrong_shanten_improvements_detection(self):
        """
        With hand 2345s1p11z bot wanted to open set on 2s,
        so after opened set we will get 25s1p11z
        it is not correct logic, because we ruined our hand
        :return:
        """
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou='2345999', honors='114446')
        player.init_hand(tiles)

        meld = self._make_meld(Meld.PON, sou='999')
        player.add_called_meld(meld)
        meld = self._make_meld(Meld.PON, honors='444')
        player.add_called_meld(meld)

        # to rebuild all caches
        player.draw_tile(self._string_to_136_tile(pin='2'))
        player.discard_tile()

        tile = self._string_to_136_tile(sou='2')
        meld, _ = table.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)


class HonitsuStrategyTestCase(unittest.TestCase, TestMixin):

    def test_should_activate_strategy(self):
        table = Table()
        player = table.player
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
        player = table.player
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
        player = table.player

        tiles = self._string_to_136_array(sou='112235589', man='24', honors='22')
        player.init_hand(tiles)

        # we don't need to call meld even if it improves our hand,
        # because we are collecting honitsu
        tile = self._string_to_136_tile(man='1')
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # any honor tile is suitable
        tile = self._string_to_136_tile(honors='2')
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)

        tile = self._string_to_136_tile(man='1')
        player.draw_tile(tile)
        tile_to_discard = player.discard_tile()

        # we are in honitsu mode, so we should discard man suits
        self.assertEqual(self._to_string([tile_to_discard]), '1m')

    def test_riichi_and_tiles_from_another_suit_in_the_hand(self):
        table = Table()
        player = table.player
        player.scores = 25000
        table.count_of_remaining_tiles = 100

        tiles = self._string_to_136_array(man='33345678', pin='22', honors='155')
        player.init_hand(tiles)

        player.draw_tile(self._string_to_136_tile(man='9'))
        tile_to_discard = player.discard_tile()

        # we don't need to go for honitsu here
        # we already in tempai
        self.assertEqual(self._to_string([tile_to_discard]), '1z')

    def test_discard_not_needed_winds(self):
        table = Table()
        player = table.player
        player.scores = 25000
        table.count_of_remaining_tiles = 100

        tiles = self._string_to_136_array(man='24', pin='4', sou='12344668', honors='36')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(sou='5'))

        table.add_discarded_tile(1, self._string_to_136_tile(honors='3'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(honors='3'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(honors='3'), False)

        tile_to_discard = player.discard_tile()

        # west was discarded three times, we don't need it
        self.assertEqual(self._to_string([tile_to_discard]), '3z')

    def test_discard_not_effective_tiles_first(self):
        table = Table()
        player = table.player
        player.scores = 25000
        table.count_of_remaining_tiles = 100

        tiles = self._string_to_136_array(man='33', pin='12788999', sou='5', honors='23')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors='6'))
        tile_to_discard = player.discard_tile()

        self.assertEqual(self._to_string([tile_to_discard]), '5s')

    def test_dont_go_for_honitsu_with_ryanmen_in_other_suit(self):
        table = Table()
        player = table.player
        strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)

        tiles = self._string_to_136_array(man='14489', sou='45', pin='67', honors='44456')
        player.init_hand(tiles)

        self.assertEqual(strategy.should_activate_strategy(), False)


class TanyaoStrategyTestCase(unittest.TestCase, TestMixin):
    
    def _make_table(self):
        table = Table()
        table.has_open_tanyao = True
        return table

    def test_should_activate_strategy_and_terminal_pon_sets(self):
        table = self._make_table()
        player = table.player
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
        table = self._make_table()
        player = table.player
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='2399', honors='11')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='345669', pin='2399')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_should_activate_strategy_and_valued_pair(self):
        table = self._make_table()
        player = table.player
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        tiles = self._string_to_136_array(man='23446679', sou='345', honors='55')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(man='23446679', sou='345', honors='22')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_should_activate_strategy_and_chitoitsu_like_hand(self):
        table = self._make_table()
        player = table.player
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

        tiles = self._string_to_136_array(sou='223388', man='3344', pin='6687')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

    def test_should_activate_strategy_and_already_completed_sided_set(self):
        table = self._make_table()
        player = table.player
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
        table = self._make_table()
        player = table.player
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
        table = self._make_table()
        player = table.player

        # with 4 shanten we don't need to aim for open tanyao
        tiles = self._string_to_136_array(man='369', pin='378', sou='3488', honors='123')
        tile = self._string_to_136_tile(sou='2')
        player.init_hand(tiles)
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # with 3 shanten we can open a hand
        tiles = self._string_to_136_array(man='236', pin='378', sou='3488', honors='123')
        tile = self._string_to_136_tile(sou='2')
        player.init_hand(tiles)
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

    def test_dont_open_hand_with_not_suitable_melds(self):
        table = self._make_table()
        player = table.player

        tiles = self._string_to_136_array(man='33355788', sou='3479', honors='3')
        tile = self._string_to_136_tile(sou='8')
        player.init_hand(tiles)
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_open_hand_and_discard_tiles_logic(self):
        table = self._make_table()
        player = table.player

        # 2345779m1p256s44z
        tiles = self._string_to_136_array(man='22345', sou='238', pin='256', honors='44')
        player.init_hand(tiles)

        # if we are in tanyao
        # we need to discard terminals and honors
        tile = self._string_to_136_tile(sou='4')
        meld, discard_option = player.try_to_call_meld(tile, True)
        discarded_tile = table.player.discard_tile(discard_option)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string([discarded_tile]), '4z')

        tile = self._string_to_136_tile(pin='5')
        player.draw_tile(tile)
        tile_to_discard = player.discard_tile()

        # we are in tanyao, so we should discard honors and terminals
        self.assertEqual(self._to_string([tile_to_discard]), '4z')

    def test_dont_count_pairs_in_already_opened_hand(self):
        table = self._make_table()
        player = table.player

        meld = self._make_meld(Meld.PON, sou='222')
        player.add_called_meld(meld)

        tiles = self._string_to_136_array(man='33556788', sou='22266')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='6')
        meld, _ = player.try_to_call_meld(tile, False)
        # even if it looks like chitoitsu we can open hand and get tempai here
        self.assertNotEqual(meld, None)

    def test_we_cant_win_with_this_hand(self):
        table = self._make_table()

        tiles = self._string_to_136_array(man='34577', sou='23', pin='233445')
        table.player.init_hand(tiles)
        meld = self._make_meld(Meld.CHI, pin='234')
        table.player.add_called_meld(meld)

        table.player.draw_tile(self._string_to_136_tile(sou='1'))
        discard = table.player.discard_tile()
        # but for already open hand we cant do tsumo
        # because we don't have a yaku here
        # so, let's do tsumogiri
        self.assertEqual(table.player.ai.previous_shanten, 0)
        self.assertEqual(self._to_string([discard]), '1s')

    def test_choose_correct_waiting(self):
        table = self._make_table()
        player = table.player

        tiles = self._string_to_136_array(man='234678', sou='234', pin='3588')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(pin='2'))

        # discard 5p and riichi
        discard = player.discard_tile()
        self.assertEqual(self._to_string([discard]), '5p')

        table = self._make_table()
        player = table.player

        meld = self._make_meld(Meld.CHI, man='234')
        player.add_called_meld(meld)

        tiles = self._string_to_136_array(man='234678', sou='234', pin='3588')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(pin='2'))

        # it is not a good idea to wait on 1-4, since we can't win on 1 with open hand
        # so let's continue to wait on 4 only
        discard = player.discard_tile()
        self.assertEqual(self._to_string([discard]), '2p')

        table = table = self._make_table()
        player = table.player

        meld = self._make_meld(Meld.CHI, man='234')
        player.add_called_meld(meld)

        tiles = self._string_to_136_array(man='234678', sou='234', pin='2388')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(sou='7'))

        # we can wait only on 1-4, so let's do it even if we can't get yaku on 1
        discard = player.discard_tile()
        self.assertEqual(self._to_string([discard]), '7s')

    def test_choose_correct_waiting_and_fist_opened_meld(self):
        table = self._make_table()
        player = table.player

        tiles = self._string_to_136_array(man='2337788', sou='345', pin='234')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(man='8')
        meld, tile_to_discard = player.try_to_call_meld(tile, False)

        discard = player.discard_tile(tile_to_discard)
        self.assertEqual(self._to_string([discard]), '2m')
