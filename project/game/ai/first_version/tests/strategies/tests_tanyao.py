# -*- coding: utf-8 -*-
import unittest

from mahjong.constants import FIVE_RED_PIN
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

        tiles = self._string_to_136_array(sou='222', man='3459', pin='233', honors='111')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(sou='222', man='3459', pin='233999')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(sou='222', man='3459', pin='233444')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), True)

    def test_should_activate_strategy_and_terminal_pairs(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

        tiles = self._string_to_136_array(sou='222', man='3459', pin='2399', honors='11')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(sou='22258', man='3566', pin='2399')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), True)

    def test_should_activate_strategy_and_valued_pair(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

        tiles = self._string_to_136_array(man='23446679', sou='222', honors='55')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(man='23446679', sou='222', honors='22')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), True)

    def test_should_activate_strategy_and_chitoitsu_like_hand(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

        tiles = self._string_to_136_array(sou='223388', man='2244', pin='6687')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), True)

    def test_should_activate_strategy_and_already_completed_sided_set(self):
        strategy = TanyaoStrategy(BaseStrategy.TANYAO, self.player)

        tiles = self._string_to_136_array(sou='123234', man='2349', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(sou='234789', man='2349', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(sou='234', man='1233459', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(sou='234', man='2227899', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(sou='234', man='2229', pin='122334')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(sou='234', man='2229', pin='234789')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), False)

        tiles = self._string_to_136_array(sou='223344', man='2229', pin='234')
        self.player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(self.player.tiles), True)

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
        tiles = self._string_to_136_array(man='269', pin='247', sou='2488', honors='123')
        tile = self._string_to_136_tile(sou='3')
        self.player.init_hand(tiles)
        meld, _ = self.player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # with 3 shanten we can open a hand
        tiles = self._string_to_136_array(man='236', pin='247', sou='2488', honors='123')
        tile = self._string_to_136_tile(sou='3')
        self.player.init_hand(tiles)
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)

    def test_dont_open_hand_with_not_suitable_melds(self):
        tiles = self._string_to_136_array(man='22255788', sou='3479', honors='3')
        tile = self._string_to_136_tile(sou='8')
        self.player.init_hand(tiles)
        meld, _ = self.player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_open_hand_and_discard_tiles_logic(self):
        tiles = self._string_to_136_array(man='22234', sou='238', pin='256', honors='44')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='4')
        meld, discard_option = self.player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string([discard_option.tile_to_discard * 4]), '4z')

        self.player.discard_tile(discard_option)

        tile = self._string_to_136_tile(pin='5')
        self.player.draw_tile(tile)
        tile_to_discard = self.player.discard_tile()

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
        tiles = self._string_to_136_array(man='22277', sou='23', pin='233445')
        self.player.init_hand(tiles)
        meld = self._make_meld(Meld.CHI, pin='234')
        self.player.add_called_meld(meld)

        self.player.draw_tile(self._string_to_136_tile(sou='1'))
        discard = self.player.discard_tile()
        # but for already open hand we cant do tsumo
        # because we don't have a yaku here
        # so, let's do tsumogiri
        self.assertEqual(self.player.ai.shanten, 0)
        self.assertEqual(self._to_string([discard]), '1s')

    def test_choose_correct_waiting(self):
        tiles = self._string_to_136_array(man='222678', sou='234', pin='3588')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(pin='2'))

        self._assert_tanyao(self.player)

        # discard 5p and riichi
        discard = self.player.discard_tile()
        self.assertEqual(self._to_string([discard]), '5p')

        meld = self._make_meld(Meld.CHI, man='234')
        self.player.add_called_meld(meld)

        tiles = self._string_to_136_array(man='234888', sou='234', pin='3588')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(pin='2'))

        # it is not a good idea to wait on 1-4, since we can't win on 1 with open hand
        # so let's continue to wait on 4 only
        discard = self.player.discard_tile()
        self.assertEqual(self._to_string([discard]), '2p')

        table = self._make_table()
        player = table.player

        meld = self._make_meld(Meld.CHI, man='678')
        player.add_called_meld(meld)

        tiles = self._string_to_136_array(man='222678', sou='234', pin='2388')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(sou='7'))

        # we can wait only on 1-4, so let's do it even if we can't get yaku on 1
        discard = player.discard_tile()
        self.assertEqual(self._to_string([discard]), '7s')

    def test_choose_correct_waiting_and_first_opened_meld(self):
        tiles = self._string_to_136_array(man='2337788', sou='222', pin='234')
        self.player.init_hand(tiles)

        self._assert_tanyao(self.player)

        tile = self._string_to_136_tile(man='8')
        meld, tile_to_discard = self.player.try_to_call_meld(tile, False)

        discard = self.player.discard_tile(tile_to_discard)
        self.assertEqual(self._to_string([discard]), '2m')

    def test_we_dont_need_to_discard_terminals_from_closed_hand(self):
        tiles = self._string_to_136_array(man='22234', sou='13588', pin='558')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(pin='5')
        self.player.draw_tile(tile)
        tile_to_discard = self.player.discard_tile()

        # our hand is closed, let's keep terminal for now
        self.assertEqual(self._to_string([tile_to_discard]), '8p')

    def test_dont_open_tanyao_with_two_non_central_doras(self):
        self.table.add_dora_indicator(self._string_to_136_tile(pin='8'))

        tiles = self._string_to_136_array(man='22234', sou='6888', pin='5599')
        self.table.player.init_hand(tiles)

        tile = self._string_to_136_tile(pin='5')
        meld, _ = self.table.player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_dont_open_tanyao_with_three_not_isolated_terminals(self):
        tiles = self._string_to_136_array(man='22256', sou='2799', pin='5579')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(pin='5')
        meld, _ = self.player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_dont_open_tanyao_with_two_not_isolated_terminals_one_shanten(self):
        tiles = self._string_to_136_array(man='22234', sou='379', pin='55579')
        self.player.init_hand(tiles)

        tile = self._string_to_136_tile(man='5')
        meld, _ = self.player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_dont_count_terminal_tiles_in_ukeire(self):
        # for closed hand let's chose tile with best ukeire
        tiles = self._string_to_136_array(man='234578', sou='235', pin='2246')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(pin='5'))
        discard = self.player.discard_tile()
        self.assertEqual(self._to_string([discard]), '5m')

        # but with opened hand we don't need to count not suitable tiles as ukeire
        tiles = self._string_to_136_array(man='234578', sou='235', pin='2246')
        self.player.init_hand(tiles)
        self.player.add_called_meld(self._make_meld(Meld.CHI, man='234'))
        self.player.draw_tile(self._string_to_136_tile(pin='5'))
        discard = self.player.discard_tile()
        self.assertEqual(self._to_string([discard]), '8m')

    def test_determine_strategy_when_we_try_to_call_meld(self):
        self.table.has_aka_dora = True

        self.table.add_dora_indicator(self._string_to_136_tile(sou='5'))
        tiles = self._string_to_136_array(man='66678', sou='6888', pin='5588')
        self.table.player.init_hand(tiles)

        # with this red five we will have 2 dora in the hand
        # and in that case we can open our hand
        meld, _ = self.table.player.try_to_call_meld(FIVE_RED_PIN, False)
        self.assertNotEqual(meld, None)

        self._assert_tanyao(self.player)

    def test_correct_discard_agari_no_yaku(self):
        tiles = self._string_to_136_array(man='23567', sou='456', pin='22244')
        self.player.init_hand(tiles)

        meld = self._make_meld(Meld.CHI, man='567')
        self.player.add_called_meld(meld)

        tile = self._string_to_136_tile(man='1')
        self.player.draw_tile(tile)
        discard = self.player.discard_tile()
        self.assertEqual(self._to_string([discard]), '1m')

    # In case we are in temporary furiten, we can't call ron, but can still
    # make chi. We assume this chi to be bad, so let's not call it.
    def test_dont_meld_agari(self):
        tiles = self._string_to_136_array(man='23567', sou='456', pin='22244')
        self.player.init_hand(tiles)

        meld = self._make_meld(Meld.CHI, man='567')
        self.player.add_called_meld(meld)

        tile = self._string_to_136_tile(man='4')
        meld, _ = self.player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

    def _make_table(self):
        table = Table()
        table.has_open_tanyao = True

        # add doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(sou='1'))
        table.add_dora_indicator(self._string_to_136_tile(man='1'))
        table.add_dora_indicator(self._string_to_136_tile(pin='1'))

        return table

    def _assert_tanyao(self, player):
        self.assertNotEqual(player.ai.current_strategy, None)
        self.assertEqual(player.ai.current_strategy.type, BaseStrategy.TANYAO)
