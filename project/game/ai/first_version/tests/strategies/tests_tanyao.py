# -*- coding: utf-8 -*-
import unittest

from mahjong.meld import Meld
from mahjong.tests_mixin import TestMixin

from game.ai.first_version.strategies.main import BaseStrategy
from game.ai.first_version.strategies.tanyao import TanyaoStrategy
from game.table import Table


class TanyaoStrategyTestCase(unittest.TestCase, TestMixin):

    def setUp(self):
        self.table = self._make_table()
        self.player = self.table.player

    def test_should_activate_strategy_and_terminal_pon_sets(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='233', honors='111')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='233999')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='233444')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_should_activate_strategy_and_terminal_pairs(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='2399', honors='11')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='345669', pin='2399')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_should_activate_strategy_and_valued_pair(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

        tiles = self._string_to_136_array(man='23446679', sou='345', honors='55')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(man='23446679', sou='345', honors='22')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_should_activate_strategy_and_chitoitsu_like_hand(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

        tiles = self._string_to_136_array(sou='223388', man='3344', pin='6687')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

    def test_should_activate_strategy_and_already_completed_sided_set(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

        tiles = self._string_to_136_array(sou='123234', man='3459', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234789', man='3459', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='1233459', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3457899', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='122334')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='234', man='3459', pin='234789')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), False)

        tiles = self._string_to_136_array(sou='223344', man='3459', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(), True)

    def test_suitable_tiles(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

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
        # with 4 shanten we don't need to aim for open tanyao
        tiles = self._string_to_136_array(man='369', pin='378', sou='3488', honors='123')
        tile = self._string_to_136_tile(sou='2')
        self.player.init_hand(tiles)
        meld, _ = self.player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # with 3 shanten we can open a hand
        tiles = self._string_to_136_array(man='236', pin='378', sou='3488', honors='123')
        tile = self._string_to_136_tile(sou='2')
        self.player.init_hand(tiles)
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

    def test_dont_open_hand_with_not_suitable_melds(self):
        tiles = self._string_to_136_array(man='33355788', sou='3479', honors='3')
        tile = self._string_to_136_tile(sou='8')
        self.player.init_hand(tiles)
        meld, _ = self.player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_open_hand_and_discard_tiles_logic(self):
        # 2345779m1p256s44z
        tiles = self._string_to_136_array(man='22345', sou='238', pin='256', honors='44')
        self.player.init_hand(tiles)

        # if we are in tanyao
        # we need to discard terminals and honors
        tile = self._string_to_136_tile(sou='4')
        meld, discard_option = self.player.try_to_call_meld(tile, True)
        discarded_tile = self.player.discard_tile(discard_option)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string([discarded_tile]), '4z')

        tile = self._string_to_136_tile(pin='5')
        self.player.draw_tile(tile)
        tile_to_discard = self.player.discard_tile()

        # we are in tanyao, so we should discard honors and terminals
        self.assertEqual(self._to_string([tile_to_discard]), '4z')

    def test_dont_count_pairs_in_already_opened_hand(self):
        meld = self._make_meld(Meld.PON, sou='222')
        self.player.add_called_meld(meld)

        tiles = self._string_to_136_array(man='33556788', sou='22266')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='6')
        meld, _ = self.player.try_to_call_meld(tile, False)
        # even if it looks like chitoitsu we can open hand and get tempai here
        self.assertNotEqual(meld, None)

    def test_we_cant_win_with_this_hand(self):
        tiles = self._string_to_136_array(man='34577', sou='23', pin='233445')
        self.player.init_hand(tiles)
        meld = self._make_meld(Meld.CHI, pin='234')
        self.player.add_called_meld(meld)

        self.player.draw_tile(self._string_to_136_tile(sou='1'))
        discard = self.player.discard_tile()
        # but for already open hand we cant do tsumo
        # because we don't have a yaku here
        # so, let's do tsumogiri
        self.assertEqual(self.player.ai.previous_shanten, 0)
        self.assertEqual(self._to_string([discard]), '1s')

    def test_choose_correct_waiting(self):
        tiles = self._string_to_136_array(man='234678', sou='234', pin='3588')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(pin='2'))

        # discard 5p and riichi
        discard = self.player.discard_tile()
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

        table = self._make_table()
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
        tiles = self._string_to_136_array(man='2337788', sou='345', pin='234')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(man='8')
        meld, tile_to_discard = self.player.try_to_call_meld(tile, False)

        discard = self.player.discard_tile(tile_to_discard)
        self.assertEqual(self._to_string([discard]), '2m')

    def _make_table(self):
        table = Table()
        table.has_open_tanyao = True
        return table
