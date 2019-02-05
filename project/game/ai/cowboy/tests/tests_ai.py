# -*- coding: utf-8 -*-
import unittest

from mahjong.meld import Meld
from mahjong.tests_mixin import TestMixin

from game.ai.first_version.strategies.main import BaseStrategy
from game.table import Table


class AITestCase(unittest.TestCase, TestMixin):

    def test_set_is_tempai_flag_to_the_player(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou='111345677', pin='45', man='56')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        player.discard_tile()
        self.assertEqual(player.in_tempai, False)

        tiles = self._string_to_136_array(sou='11145677', pin='345', man='56')
        tile = self._string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        player.discard_tile()
        self.assertEqual(player.in_tempai, True)

    def test_not_open_hand_in_riichi(self):
        table = Table()
        player = table.player

        player.in_riichi = True

        tiles = self._string_to_136_array(sou='12368', pin='2358', honors='4455')
        tile = self._string_to_136_tile(honors='5')
        player.init_hand(tiles)
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_not_open_hand_in_defence_mode(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou='12368', pin='2358', honors='4455')
        player.init_hand(tiles)

        table.add_called_riichi(1)

        tile = self._string_to_136_tile(honors='5')
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

    def test_chose_right_set_to_open_hand(self):
        """
        Different test cases to open hand and chose correct set to open hand.
        Based on real examples of incorrect opened hands
        """
        table = Table()
        table.has_open_tanyao = True
        player = table.player

        tiles = self._string_to_136_array(man='23455', pin='3445678', honors='1')
        tile = self._string_to_136_tile(man='5')
        player.init_hand(tiles)

        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(self._to_string(meld.tiles), '555m')

        table = Table()
        player = table.player
        tiles = self._string_to_136_array(man='335666', pin='22', sou='345', honors='55')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(man='4')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '345m')

        table = Table()
        table.has_open_tanyao = True
        player = table.player
        tiles = self._string_to_136_array(man='23557', pin='556788', honors='22')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(pin='5')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(self._to_string(meld.tiles), '555p')

    def test_not_open_hand_for_not_needed_set(self):
        """
        We don't need to open hand if it is not improve the hand.
        It was a bug related to it
        """
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='22457', sou='12234', pin='9', honors='55')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='3')
        meld, discard_option = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string(meld.tiles), '123s')
        player.add_called_meld(meld)
        player.discard_tile(discard_option)

        tile = self._string_to_136_tile(sou='3')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertIsNone(meld)

    def test_chose_strategy_and_reset_strategy(self):
        table = Table()
        table.has_open_tanyao = True
        player = table.player

        tiles = self._string_to_136_array(man='33355788', sou='3479', honors='3')
        player.init_hand(tiles)
        self.assertEqual(player.ai.current_strategy.type, BaseStrategy.TANYAO)

        # we draw a tile that will change our selected strategy
        tile = self._string_to_136_tile(sou='8')
        player.draw_tile(tile)
        self.assertEqual(player.ai.current_strategy, None)

        tiles = self._string_to_136_array(man='33355788', sou='3479', honors='3')
        player.init_hand(tiles)
        self.assertEqual(player.ai.current_strategy.type, BaseStrategy.TANYAO)

        # for already opened hand we don't need to give up on selected strategy
        meld = Meld()
        meld.tiles = [1, 2, 3]
        player.add_called_meld(meld)
        tile = self._string_to_136_tile(sou='8')
        player.draw_tile(tile)
        self.assertEqual(player.ai.current_strategy.type, BaseStrategy.TANYAO)

    def test_remaining_tiles_and_enemy_discard(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='123456789', sou='167', honors='77')
        player.init_hand(tiles)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.tiles_count, 8)

        player.table.add_discarded_tile(1, self._string_to_136_tile(sou='5'), False)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.tiles_count, 7)

        player.table.add_discarded_tile(2, self._string_to_136_tile(sou='5'), False)
        player.table.add_discarded_tile(3, self._string_to_136_tile(sou='8'), False)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.tiles_count, 5)

    def test_remaining_tiles_and_opened_meld(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='123456789', sou='167', honors='77')
        player.init_hand(tiles)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.tiles_count, 8)

        # was discard and set was opened
        tile = self._string_to_136_tile(sou='8')
        player.table.add_discarded_tile(3, tile, False)
        meld = self._make_meld(Meld.PON, sou='888')
        meld.called_tile = tile
        player.table.add_called_meld(3, meld)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.tiles_count, 5)

        # was discard and set was opened
        tile = self._string_to_136_tile(sou='3')
        player.table.add_discarded_tile(2, tile, False)
        meld = self._make_meld(Meld.PON, sou='345')
        meld.called_tile = tile
        player.table.add_called_meld(2, meld)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.tiles_count, 4)

    def test_remaining_tiles_and_dora_indicators(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='123456789', sou='167', honors='77')
        player.init_hand(tiles)

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.tiles_count, 8)

        table.add_dora_indicator(self._string_to_136_tile(sou='8'))

        results, shanten = player.ai.calculate_outs(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.tiles_count, 7)

    def test_using_tiles_of_different_suit_for_chi(self):
        """
        It was a bug related to it, when bot wanted to call 9p12s chi :(
        """
        table = Table()
        player = table.player

        # 16m2679p1348s111z
        tiles = [0, 21, 41, 56, 61, 70, 74, 80, 84, 102, 108, 110, 111]
        player.init_hand(tiles)

        # 2s
        tile = 77
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertIsNotNone(meld)

    def test_upgrade_opened_pon_to_kan(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='34445', sou='123456', pin='89')
        player.init_hand(tiles)
        tile = self._string_to_136_tile(man='4')
        player.draw_tile(tile)

        self.assertEqual(player.should_call_kan(tile, False), None)

        player.add_called_meld(self._make_meld(Meld.PON, man='444'))

        self.assertEqual(len(player.melds), 1)
        self.assertEqual(len(player.tiles), 14)
        self.assertEqual(player.should_call_kan(tile, False), Meld.CHANKAN)

        player.discard_tile()
        player.draw_tile(tile)
        player.add_called_meld(self._make_meld(Meld.CHANKAN, man='4444'))

        self.assertEqual(len(player.melds), 1)
        self.assertEqual(player.melds[0].type, Meld.CHANKAN)
        self.assertEqual(len(player.tiles), 13)

    def test_call_closed_kan(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='12223', sou='111456', pin='12')
        player.init_hand(tiles)
        tile = self._string_to_136_tile(man='2')
        player.draw_tile(tile)

        # it is pretty stupid to call closed kan with 2m
        self.assertEqual(player.should_call_kan(tile, False), None)

        tiles = self._string_to_136_array(man='12223', sou='111456', pin='12')
        player.init_hand(tiles)
        tile = self._string_to_136_tile(sou='1')
        player.draw_tile(tile)

        # call closed kan with 1s is fine
        self.assertEqual(player.should_call_kan(tile, False), Meld.KAN)

    def test_opened_kan(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='299', sou='111456', pin='1', honors='111')
        player.init_hand(tiles)

        # to rebuild all caches
        player.draw_tile(self._string_to_136_tile(pin='9'))
        player.discard_tile()

        # our hand is closed, we don't need to call opened kan here
        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(player.should_call_kan(tile, True), None)

        player.add_called_meld(self._make_meld(Meld.PON, honors='111'))

        # our hand is open, but it is not tempai
        # we don't need to open kan here
        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(player.should_call_kan(tile, True), None)

        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='2399', sou='111456', honors='111')
        player.init_hand(tiles)
        player.add_called_meld(self._make_meld(Meld.PON, honors='111'))

        # to rebuild all caches
        player.draw_tile(self._string_to_136_tile(pin='9'))
        player.discard_tile()

        # our hand is open, in tempai and with a good wait
        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(player.should_call_kan(tile, True), Meld.KAN)

    def test_closed_kan_and_riichi(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        kan_tiles = self._string_to_136_array(pin='7777')
        tiles = self._string_to_136_array(pin='568', sou='1235788') + kan_tiles[:3]
        player.init_hand(tiles)

        # +3 to avoid tile duplication of 7 pin
        tile = kan_tiles[3]
        player.draw_tile(tile)

        kan_type = player.should_call_kan(tile, False)
        self.assertEqual(kan_type, Meld.KAN)

        meld = Meld()
        meld.type = Meld.KAN
        meld.tiles = kan_tiles
        meld.called_tile = tile
        meld.who = 0
        meld.from_who = 0
        meld.opened = False

        # replacement from the dead wall
        player.draw_tile(self._string_to_136_tile(pin='4'))
        table.add_called_meld(meld.who, meld)
        discard = player.discard_tile()

        self.assertEqual(self._to_string([discard]), '8p')
        self.assertEqual(player.can_call_riichi(), True)

        # with closed kan we can't call riichi
        player.melds[0].opened = True
        self.assertEqual(player.can_call_riichi(), False)

    def test_dont_call_kan_in_defence_mode(self):
        table = Table()

        tiles = self._string_to_136_array(man='12589', sou='111459', pin='12')
        table.player.init_hand(tiles)

        table.add_called_riichi(1)

        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(table.player.should_call_kan(tile, False), None)
