# -*- coding: utf-8 -*-
import unittest

from mahjong.tests_mixin import TestMixin

from game.table import Table


class CallRiichiTestCase(unittest.TestCase, TestMixin):

    def test_dont_call_riichi_with_yaku_and_central_tanki_wait(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        tiles = self._string_to_136_array(sou='234567', pin='234567', man='4')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(man='5'))
        player.discard_tile()

        self.assertEqual(player.can_call_riichi(), False)

    def test_call_riichi_and_penchan_wait(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        tiles = self._string_to_136_array(sou='11223', pin='234567', man='66')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(man='9'))
        player.discard_tile()

        self.assertEqual(player.can_call_riichi(), True)

    def test_dont_call_riichi_expensive_damaten_with_yaku(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        table.add_dora_indicator(self._string_to_136_tile(man='7'))
        table.add_dora_indicator(self._string_to_136_tile(man='5'))
        table.add_dora_indicator(self._string_to_136_tile(sou='1'))

        # tanyao pinfu sanshoku dora 4 - this is damaten baiman, let's not riichi it
        tiles = self._string_to_136_array(man='67888', sou='678', pin='34678')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors='3'))
        player.discard_tile()
        self.assertEqual(player.can_call_riichi(), False)

        # let's test lots of doras hand, tanyao dora 8, also damaten baiman
        tiles = self._string_to_136_array(man='666888', sou='22', pin='34678')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors='3'))
        player.discard_tile()
        self.assertEqual(player.can_call_riichi(), False)

        # chuuren
        tiles = self._string_to_136_array(man='1112345678999')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors='3'))
        player.discard_tile()
        self.assertEqual(player.can_call_riichi(), False)

    def test_riichi_expensive_hand_without_yaku(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        table.add_dora_indicator(self._string_to_136_tile(man='1'))
        table.add_dora_indicator(self._string_to_136_tile(sou='1'))
        table.add_dora_indicator(self._string_to_136_tile(pin='1'))

        tiles = self._string_to_136_array(man='222', sou='22278', pin='22789')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors='3'))
        player.discard_tile()
        self.assertEqual(player.can_call_riichi(), True)

    def test_riichi_tanki_honor_without_yaku(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        table.add_dora_indicator(self._string_to_136_tile(man='2'))
        table.add_dora_indicator(self._string_to_136_tile(sou='6'))

        tiles = self._string_to_136_array(man='345678', sou='789', pin='123', honors='2')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors='3'))
        player.discard_tile()
        self.assertEqual(player.can_call_riichi(), True)

    def test_riichi_tanki_honor_chiitoitsu(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        player = table.player
        player.scores = 25000

        tiles = self._string_to_136_array(man='22336688', sou='99', pin='99', honors='2')
        player.init_hand(tiles)
        player.draw_tile(self._string_to_136_tile(honors='3'))
        player.discard_tile()
        self.assertEqual(player.can_call_riichi(), True)
