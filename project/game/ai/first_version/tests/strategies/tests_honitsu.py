# -*- coding: utf-8 -*-
import unittest

from mahjong.tests_mixin import TestMixin
from mahjong.meld import Meld

from game.ai.first_version.strategies.honitsu import HonitsuStrategy
from game.ai.first_version.strategies.main import BaseStrategy
from game.table import Table


class HonitsuStrategyTestCase(unittest.TestCase, TestMixin):

    def test_should_activate_strategy(self):
        table = Table()
        player = table.player
        strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)

        table.add_dora_indicator(self._string_to_136_tile(pin='1'))
        table.add_dora_indicator(self._string_to_136_tile(honors='5'))

        tiles = self._string_to_136_array(sou='12355', man='12389', honors='123')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # many tiles in one suit and yakuhai pair, but still many useless winds
        tiles = self._string_to_136_array(sou='12355', man='23', pin='68', honors='2355')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # many tiles in one suit and yakuhai pair and another honor pair, so
        # now this is honitsu
        tiles = self._string_to_136_array(sou='12355', man='238', honors='22355')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        # same conditions, but ready suit with dora in another suit, so no honitsu
        tiles = self._string_to_136_array(sou='12355', pin='234', honors='22355')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # same conditions, but we have a pon of yakuhai doras, we shouldn't
        # force honitsu with this hand
        tiles = self._string_to_136_array(sou='12355', pin='238', honors='22666')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # if we have a complete set with dora, we shouldn't go for honitsu
        tiles = self._string_to_136_array(sou='11123688', pin='123', honors='55')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # even if the set may be interpreted as two forms
        tiles = self._string_to_136_array(sou='1223688', pin='2334', honors='55')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # even if the set may be interpreted as two forms v2
        tiles = self._string_to_136_array(sou='1223688', pin='2345', honors='55')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # if we have a long form with dora, we shouldn't go for honitsu
        tiles = self._string_to_136_array(sou='1223688', pin='2333', honors='55')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

    def test_suitable_tiles(self):
        table = Table()
        player = table.player
        strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)

        tiles = self._string_to_136_array(sou='12355', man='238', honors='23455')
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

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

        tiles = self._string_to_136_array(sou='112235589', man='23', honors='22')
        player.init_hand(tiles)

        # we don't need to call meld even if it improves our hand,
        # because we are aim for honitsu
        tile = self._string_to_136_tile(man='1')
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # any honor tile is suitable
        tile = self._string_to_136_tile(honors='2')
        meld, discard_option = player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string([discard_option.tile_to_discard * 4]), '2m')

        player.discard_tile(discard_option)

        tile = self._string_to_136_tile(man='1')
        player.draw_tile(tile)
        tile_to_discard, _ = player.discard_tile()

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
        tile_to_discard, _ = player.discard_tile()

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

        tile_to_discard, _ = player.discard_tile()

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
        tile_to_discard, _ = player.discard_tile()

        self.assertEqual(self._to_string([tile_to_discard]), '5s')

    def test_open_yakuhai_same_shanten(self):
        table = Table()
        player = table.player
        player.scores = 25000
        table.count_of_remaining_tiles = 100

        tiles = self._string_to_136_array(man='34556778', pin='3', sou='78', honors='77')
        player.init_hand(tiles)

        meld = self._make_meld(Meld.CHI, man='345')
        player.add_called_meld(meld)

        strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        tile = self._string_to_136_tile(honors='7')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string(meld.tiles), '777z')

    def test_open_hand_and_not_go_for_chiitoitsu(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou='1122559', honors='134557', pin='4')
        player.init_hand(tiles)

        tile, _ = player.discard_tile()
        self.assertEqual(self._to_string([tile]), '4p')

        tile = self._string_to_136_tile(honors='5')
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string(meld.tiles), '555z')

    def test_open_suit_same_shanten(self):
        table = Table()
        player = table.player
        player.scores = 25000
        table.count_of_remaining_tiles = 100

        tiles = self._string_to_136_array(man='1134556', pin='3', sou='78', honors='777')
        player.init_hand(tiles)

        meld = self._make_meld(Meld.CHI, man='345')
        player.add_called_meld(meld)

        strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        tile = self._string_to_136_tile(man='1')
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string(meld.tiles), '111m')
