# -*- coding: utf-8 -*-
import unittest

from game.ai.strategies.chiitoitsu import ChiitoitsuStrategy
from game.ai.strategies.main import BaseStrategy
from game.table import Table
from mahjong.tests_mixin import TestMixin


class ChiitoitsuStrategyTestCase(unittest.TestCase, TestMixin):
    def test_should_activate_strategy(self):
        table = Table()
        player = table.player
        strategy = ChiitoitsuStrategy(BaseStrategy.CHIITOITSU, player)

        # obvious chiitoitsu, let's activate
        tiles = self._string_to_136_array(sou="2266", man="3399", pin="289", honors="11")
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors="6"))
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        # less than 5 pairs, don't activate
        tiles = self._string_to_136_array(sou="2266", man="3389", pin="289", honors="11")
        player.draw_tile(self._string_to_136_tile(honors="6"))
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        # 5 pairs, but we are already tempai, let's no consider this hand as chiitoitsu
        tiles = self._string_to_136_array(sou="234", man="223344", pin="5669")
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(pin="5"))
        player.discard_tile()
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

        tiles = self._string_to_136_array(sou="234", man="22334455669")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), False)

    def test_dont_call_meld(self):
        table = Table()
        player = table.player
        strategy = ChiitoitsuStrategy(BaseStrategy.CHIITOITSU, player)

        tiles = self._string_to_136_array(sou="112234", man="2334499")
        player.init_hand(tiles)
        self.assertEqual(strategy.should_activate_strategy(player.tiles), True)

        tile = self._string_to_136_tile(man="9")
        meld, _ = player.try_to_call_meld(tile, True)
        self.assertEqual(meld, None)

    def test_keep_chiitoitsu_tempai(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou="113355", man="22669", pin="99")
        player.init_hand(tiles)

        player.draw_tile(self._string_to_136_tile(man="6"))

        discard = player.discard_tile()
        self.assertEqual(self._to_string([discard]), "6m")

    def test_5_pairs_yakuhai_not_chiitoitsu(self):
        table = Table()
        player = table.player

        table.add_dora_indicator(self._string_to_136_tile(sou="9"))
        table.add_dora_indicator(self._string_to_136_tile(sou="1"))

        tiles = self._string_to_136_array(sou="112233", pin="16678", honors="66")
        player.init_hand(tiles)

        tile = self._string_to_136_tile(honors="6")
        meld, _ = player.try_to_call_meld(tile, True)

        self.assertNotEqual(player.ai.current_strategy.type, BaseStrategy.CHIITOITSU)

        self.assertEqual(player.ai.current_strategy.type, BaseStrategy.YAKUHAI)

        self.assertNotEqual(meld, None)

    def chiitoitsu_tanyao_tempai(self):
        table = Table()
        player = table.player

        tiles = self._string_to_136_array(sou="223344", pin="788", man="4577")
        player.init_hand(tiles)

        player.draw_tile(self._string_to_136_tile(man="4"))

        discard = player.discard_tile()
        discard_correct = self._to_string([discard]) == "7p" or self._to_string([discard]) == "5m"
        self.assertEqual(discard_correct, True)
