# -*- coding: utf-8 -*-
import unittest

from game.ai.strategies.chinitsu import ChinitsuStrategy
from game.ai.strategies.main import BaseStrategy
from game.table import Table
from mahjong.meld import Meld
from mahjong.tests_mixin import TestMixin


class ChinitsuStrategyTestCase(unittest.TestCase, TestMixin):
    def test_should_activate_strategy(self):
        table = Table()
        player = table.player
        strategy = ChinitsuStrategy(BaseStrategy.CHINITSU, player)

        table.add_dora_indicator(self._string_to_136_tile(pin="1"))
        table.add_dora_indicator(self._string_to_136_tile(man="1"))
        table.add_dora_indicator(self._string_to_136_tile(sou="8"))

        tiles = self._string_to_136_array(sou="12355", man="34589", honors="1234")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        tiles = self._string_to_136_array(sou="12355", man="458", honors="112345")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # we shouldn't go for chinitsu if we have a valued pair or pon
        tiles = self._string_to_136_array(sou="111222578", man="8", honors="5556")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        tiles = self._string_to_136_array(sou="1112227788", man="7", honors="556")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # if we have a pon of non-valued honors, this is not chinitsu
        tiles = self._string_to_136_array(sou="1112224688", honors="2224")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # if we have just a pair of non-valued tiles, we can go for chinitsu
        # if we have 11 chinitsu tiles and it's early
        tiles = self._string_to_136_array(sou="11122234688", honors="224")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        # if we have a complete set with dora, we shouldn't go for chinitsu
        tiles = self._string_to_136_array(sou="1112223688", pin="1239")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # even if the set may be interpreted as two forms
        tiles = self._string_to_136_array(sou="111223688", pin="23349")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # even if the set may be interpreted as two forms v2
        tiles = self._string_to_136_array(sou="111223688", pin="23459")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # if we have a long form with dora, we shouldn't go for chinitsu
        tiles = self._string_to_136_array(sou="111223688", pin="23339")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # buf it it's just a ryanmen - no problem
        tiles = self._string_to_136_array(sou="1112223688", pin="238", man="9")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        # we have three non-isolated doras in other suits, this is not chinitsu
        tiles = self._string_to_136_array(sou="111223688", man="22", pin="239")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # we have two non-isolated doras in other suits and no doras in our suit
        # this is not chinitsu
        tiles = self._string_to_136_array(sou="111223688", man="24", pin="249")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # we have two non-isolated doras in other suits and 1 shanten, not chinitsu
        tiles = self._string_to_136_array(sou="111222789", man="23", pin="239")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # we don't want to open on 9th tile into chinitsu, but it's ok to
        # switch to chinitsu if we get in from the wall
        tiles = self._string_to_136_array(sou="11223578", man="57", pin="4669")
        player.init_hand(tiles)
        # plus one tile to open hand
        tiles = self._string_to_136_array(sou="112223578", man="57", pin="466")
        self.assertEqual(strategy.should_activate_strategy(tiles), False)
        # but now let's init hand with these tiles, we can now slowly move to chinitsu
        tiles = self._string_to_136_array(sou="112223578", man="57", pin="466")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(tiles), True)

    def test_suitable_tiles(self):
        table = Table()
        player = table.player
        strategy = ChinitsuStrategy(BaseStrategy.CHINITSU, player)

        tiles = self._string_to_136_array(sou="111222479", man="78", honors="12")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        tile = self._string_to_136_tile(man="1")
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(pin="1")
        self.assertEqual(strategy.is_tile_suitable(tile), False)

        tile = self._string_to_136_tile(sou="1")
        self.assertEqual(strategy.is_tile_suitable(tile), True)

        tile = self._string_to_136_tile(honors="1")
        self.assertEqual(strategy.is_tile_suitable(tile), False)

    def test_open_suit_same_shanten(self):
        table = Table()
        player = table.player
        player.scores = 25000
        table.count_of_remaining_tiles = 100

        tiles = self._string_to_136_array(man="1134556999", pin="3", sou="78")
        player.init_hand(tiles)

        meld = self._make_meld(Meld.CHI, man="345")
        player.add_called_meld(meld)

        strategy = ChinitsuStrategy(BaseStrategy.CHINITSU, player)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        tile = self._string_to_136_tile(man="1")
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string(meld.tiles), "111m")

    def test_correct_discard_agari_no_yaku(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(man="111234677889", sou="1", pin="")
        player.init_hand(tiles)

        meld = self._make_meld(Meld.CHI, man="789")
        player.add_called_meld(meld)

        tile = self._string_to_136_tile(sou="1")
        player.draw_tile(tile)
        discard = player.discard_tile()
        self.assertEqual(self._to_string([discard]), "1s")

    def test_open_suit_agari_no_yaku(self):
        table = Table()
        player = table.player
        player.scores = 25000
        table.count_of_remaining_tiles = 100

        tiles = self._string_to_136_array(man="11123455589", pin="22")
        player.init_hand(tiles)

        meld = self._make_meld(Meld.CHI, man="234")
        player.add_called_meld(meld)

        strategy = ChinitsuStrategy(BaseStrategy.CHINITSU, player)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        tile = self._string_to_136_tile(man="7")
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertNotEqual(meld, None)
        self.assertEqual(self._to_string(meld.tiles), "789m")
