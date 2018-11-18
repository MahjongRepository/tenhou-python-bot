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

        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(pin='2'))
        table.add_dora_indicator(self._string_to_136_tile(pin='3'))

        tiles = self._string_to_136_array(man='23455', pin='3445678', honors='1')
        tile = self._string_to_136_tile(man='5')
        player.init_hand(tiles)

        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(self._to_string(meld.tiles), '555m')

        table = Table()
        player = table.player
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='5'))
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
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='1'))
        table.add_dora_indicator(self._string_to_136_tile(man='4'))
        tiles = self._string_to_136_array(man='23557', pin='556788', honors='22')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(pin='5')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.PON)
        self.assertEqual(self._to_string(meld.tiles), '555p')

        table = Table()
        table.has_open_tanyao = True
        player = table.player
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='4'))
        table.add_dora_indicator(self._string_to_136_tile(pin='5'))
        tiles = self._string_to_136_array(man='3556', pin='234668', sou='248')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(man='4')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '345m')

        table = Table()
        table.has_open_tanyao = True
        player = table.player
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='4'))
        table.add_dora_indicator(self._string_to_136_tile(pin='5'))
        tiles = self._string_to_136_array(man='3445', pin='234668', sou='248')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(man='4')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '345m')

        table = Table()
        table.has_open_tanyao = True
        player = table.player
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='7'))
        tiles = self._string_to_136_array(man='567888', pin='788', sou='3456')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='4')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '456s')

        tile = self._string_to_136_tile(sou='5')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '345s')

        table = Table()
        table.has_open_tanyao = True
        player = table.player
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='7'))
        tiles = self._string_to_136_array(man='567888', pin='788', sou='2345')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='4')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '234s')

    def test_chose_right_set_to_open_hand_dora(self):
        table = Table()
        table.has_open_tanyao = True
        table.has_aka_dora = False
        player = table.player
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='7'))
        table.add_dora_indicator(self._string_to_136_tile(sou='1'))
        tiles = self._string_to_136_array(man='3456788', sou='245888')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='3')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '234s')

        table = Table()
        table.has_open_tanyao = True
        table.has_aka_dora = False
        player = table.player
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='7'))
        table.add_dora_indicator(self._string_to_136_tile(sou='4'))
        tiles = self._string_to_136_array(man='3456788', sou='245888')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='3')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '345s')

        table = Table()
        table.has_open_tanyao = True
        table.has_aka_dora = True
        player = table.player
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='7'))
        # 5 from string is always aka
        tiles = self._string_to_136_array(man='3456788', sou='245888')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='3')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '345s')

        table = Table()
        table.has_open_tanyao = True
        table.has_aka_dora = True
        player = table.player
        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='7'))
        table.add_dora_indicator(self._string_to_136_tile(sou='1'))
        table.add_dora_indicator(self._string_to_136_tile(sou='4'))
        # double dora versus regular dora, we should keep double dora
        tiles = self._string_to_136_array(man='3456788', sou='245888')
        player.init_hand(tiles)

        tile = self._string_to_136_tile(sou='3')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(meld.type, Meld.CHI)
        self.assertEqual(self._to_string(meld.tiles), '345s')

    def test_not_open_hand_for_not_needed_set(self):
        """
        We don't need to open hand if it is not improve the hand.
        It was a bug related to it
        """
        table = Table()
        player = table.player

        table.dora_indicators.append(self._string_to_136_tile(honors='7'))
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

        # add 3 doras so we are sure to go for tanyao
        table.add_dora_indicator(self._string_to_136_tile(man='2'))

        tiles = self._string_to_136_array(man='33355788', sou='3479', honors='3')
        player.init_hand(tiles)
        self.assertNotEqual(player.ai.current_strategy, None)
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
        self.assertNotEqual(player.ai.current_strategy, None)
        self.assertEqual(player.ai.current_strategy.type, BaseStrategy.TANYAO)

    def test_remaining_tiles_and_enemy_discard(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='123456789', sou='167', honors='77')
        player.init_hand(tiles)

        results, shanten = player.ai.hand_builder.find_discard_options(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.ukeire, 8)

        player.table.add_discarded_tile(1, self._string_to_136_tile(sou='5'), False)

        results, shanten = player.ai.hand_builder.find_discard_options(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.ukeire, 7)

        player.table.add_discarded_tile(2, self._string_to_136_tile(sou='5'), False)
        player.table.add_discarded_tile(3, self._string_to_136_tile(sou='8'), False)

        results, shanten = player.ai.hand_builder.find_discard_options(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.ukeire, 5)

    def test_remaining_tiles_and_opened_meld(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='123456789', sou='167', honors='77')
        player.init_hand(tiles)

        results, shanten = player.ai.hand_builder.find_discard_options(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.ukeire, 8)

        # was discard and set was opened
        tile = self._string_to_136_tile(sou='8')
        player.table.add_discarded_tile(3, tile, False)
        meld = self._make_meld(Meld.PON, sou='888')
        meld.called_tile = tile
        player.table.add_called_meld(3, meld)

        results, shanten = player.ai.hand_builder.find_discard_options(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.ukeire, 5)

        # was discard and set was opened
        tile = self._string_to_136_tile(sou='3')
        player.table.add_discarded_tile(2, tile, False)
        meld = self._make_meld(Meld.PON, sou='345')
        meld.called_tile = tile
        player.table.add_called_meld(2, meld)

        results, shanten = player.ai.hand_builder.find_discard_options(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.ukeire, 4)

    def test_remaining_tiles_and_dora_indicators(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='123456789', sou='167', honors='77')
        player.init_hand(tiles)

        results, shanten = player.ai.hand_builder.find_discard_options(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.ukeire, 8)

        table.add_dora_indicator(self._string_to_136_tile(sou='8'))

        results, shanten = player.ai.hand_builder.find_discard_options(tiles, tiles)
        result = [x for x in results if x.tile_to_discard == self._string_to_34_tile(sou='1')][0]
        self.assertEqual(result.ukeire, 7)

    def test_using_tiles_of_different_suit_for_chi(self):
        """
        It was a bug related to it, when bot wanted to call 9p12s chi :(
        """
        table = Table()
        player = table.player

        # 16m2679p1348s111z
        table.dora_indicators.append(self._string_to_136_tile(honors='4'))
        tiles = [0, 21, 41, 56, 61, 70, 74, 80, 84, 102, 108, 110, 111]
        player.init_hand(tiles)

        # 2s
        tile = 77
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertIsNotNone(meld)

    def test_upgrade_opened_pon_to_kan(self):
        table = Table()
        table.count_of_remaining_tiles = 10

        tiles = self._string_to_136_array(man='34445', sou='123456', pin='89')
        table.player.init_hand(tiles)
        tile = self._string_to_136_tile(man='4')

        self.assertEqual(table.player.should_call_kan(tile, False), None)

        table.player.add_called_meld(self._make_meld(Meld.PON, man='444'))

        self.assertEqual(len(table.player.melds), 1)
        self.assertEqual(len(table.player.tiles), 13)
        self.assertEqual(table.player.should_call_kan(tile, False), Meld.CHANKAN)

    def test_call_closed_kan(self):
        table = Table()
        table.count_of_remaining_tiles = 10

        tiles = self._string_to_136_array(man='12223', sou='111456', pin='12')
        table.player.init_hand(tiles)
        tile = self._string_to_136_tile(man='2')

        # it is pretty stupid to call closed kan with 2m
        self.assertEqual(table.player.should_call_kan(tile, False), None)

        tiles = self._string_to_136_array(man='12223', sou='111456', pin='12')
        table.player.init_hand(tiles)
        tile = self._string_to_136_tile(sou='1')

        # call closed kan with 1s is fine
        self.assertEqual(table.player.should_call_kan(tile, False), Meld.KAN)

    def test_opened_kan(self):
        table = Table()
        table.count_of_remaining_tiles = 10

        tiles = self._string_to_136_array(man='299', sou='111456', pin='1', honors='111')
        table.player.init_hand(tiles)

        # to rebuild all caches
        table.player.draw_tile(self._string_to_136_tile(pin='9'))
        table.player.discard_tile()

        # our hand is closed, we don't need to call opened kan here
        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(table.player.should_call_kan(tile, True), None)

        table.player.add_called_meld(self._make_meld(Meld.PON, honors='111'))

        # our hand is open, but it is not tempai
        # we don't need to open kan here
        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(table.player.should_call_kan(tile, True), None)

        table = Table()
        table.count_of_remaining_tiles = 10

        tiles = self._string_to_136_array(man='2399', sou='111456', honors='111')
        table.player.init_hand(tiles)
        table.player.add_called_meld(self._make_meld(Meld.PON, honors='111'))

        # to rebuild all caches
        table.player.draw_tile(self._string_to_136_tile(pin='9'))
        table.player.discard_tile()

        # our hand is open, in tempai and with a good wait
        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(table.player.should_call_kan(tile, True), Meld.KAN)

    def test_dont_call_kan_in_defence_mode(self):
        table = Table()

        tiles = self._string_to_136_array(man='12589', sou='111459', pin='12')
        table.player.init_hand(tiles)

        table.add_called_riichi(1)

        tile = self._string_to_136_tile(sou='1')
        self.assertEqual(table.player.should_call_kan(tile, False), None)

    def test_closed_kan_and_wrong_shanten_number_calculation(self):
        """
        Bot tried to call riichi with 567m666p14578s + [9999s] hand
        """
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='56', sou='14578999', pin='666')
        player.init_hand(tiles)
        tile = self._string_to_136_tile(man='7')
        player.melds.append(self._make_meld(Meld.KAN, False, sou='9999'))
        player.draw_tile(tile)
        player.discard_tile()

        # bot not in the tempai, because all 9s in the closed kan
        self.assertEqual(player.ai.shanten, 1)

    def test_closed_kan_and_not_necessary_call(self):
        """
        Bot tried to call closed kan with 568m669p1478999s + 9s hand
        """
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man='568', sou='1478999', pin='669')
        player.init_hand(tiles)
        tile = self._string_to_136_tile(sou='9')

        self.assertEqual(player.should_call_kan(tile, False), None)

    def test_closed_kan_same_shanten_bad_ukeire(self):
        """
        Bot tried to call closed kan with 4557888899m2z + 333m melded hand
        Shanten number is the same, but ukeire becomes much worse
        """
        table = Table()
        player = table.player

        table.add_dora_indicator(self._string_to_136_tile(honors='2'))
        table.add_dora_indicator(self._string_to_136_tile(honors='4'))

        table.count_of_remaining_tiles = 10

        tiles = self._string_to_136_array(man='333455788899', honors='3')
        player.init_hand(tiles)
        player.melds.append(self._make_meld(Meld.PON, man='333'))

        tile = self._string_to_136_tile(man='8')

        self.assertEqual(player.should_call_kan(tile, False), None)

    def test_closed_kan_same_shanten_same_ukeire(self):
        table = Table()
        player = table.player

        table.add_dora_indicator(self._string_to_136_tile(honors='2'))
        table.add_dora_indicator(self._string_to_136_tile(honors='4'))

        table.count_of_remaining_tiles = 10

        tiles = self._string_to_136_array(man='3334557889', honors='333')
        player.init_hand(tiles)
        player.melds.append(self._make_meld(Meld.PON, man='333'))

        tile = self._string_to_136_tile(honors='3')

        self.assertEqual(player.should_call_kan(tile, False), Meld.KAN)

    def test_kan_crash(self):
        """
        This was a crash in real game
        related with open kan logic and agari without yaku state
        """
        table = Table()
        table.count_of_remaining_tiles = 10

        tiles = self._string_to_136_array(man='456', pin='78999', sou='666', honors='33')
        table.player.init_hand(tiles)
        table.player.add_called_meld(self._make_meld(Meld.PON, sou='666'))
        tile = self._string_to_136_tile(pin='9')

        self.assertEqual(table.player.should_call_kan(tile, False), None)
