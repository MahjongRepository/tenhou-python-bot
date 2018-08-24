# -*- coding: utf-8 -*-
import unittest

from mahjong.tests_mixin import TestMixin

from game.ai.first_version.strategies.honitsu import HonitsuStrategy
from game.ai.first_version.strategies.main import BaseStrategy
from game.table import Table


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

        tiles = self._string_to_136_array(sou='112235589', man='23', honors='22')
        player.init_hand(tiles)

        # we don't need to call meld even if it improves our hand,
        # because we are aim for honitsu
        tile = self._string_to_136_tile(man='1')
        meld, _ = player.try_to_call_meld(tile, False)
        self.assertEqual(meld, None)

        # any honor tile is suitable
        tile = self._string_to_136_tile(honors='2')
        meld, tile_to_discard = player.try_to_call_meld(tile, False)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string([tile_to_discard * 4]), '2m')

        player.discard_tile(tile_to_discard * 4)

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



