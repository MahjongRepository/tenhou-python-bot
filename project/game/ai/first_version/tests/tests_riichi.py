# -*- coding: utf-8 -*-
import unittest

from mahjong.tests_mixin import TestMixin
from mahjong.tile import Tile

from game.table import Table


class CallRiichiTestCase(unittest.TestCase, TestMixin):
    def _make_table(self, dora_indicators=None):
        self.table = Table()
        self.table.count_of_remaining_tiles = 60
        self.player = self.table.player
        self.player.scores = 25000

        # with that we don't have daburi anymore
        self.player.round_step = 1

        if dora_indicators:
            for x in dora_indicators:
                self.table.add_dora_indicator(x)

    def test_dont_call_riichi_with_yaku_and_central_tanki_wait(self):
        self._make_table()

        tiles = self._string_to_136_array(sou='234567', pin='234567', man='4')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(man='5'))
        self.player.discard_tile()

        self.assertEqual(self.player.can_call_riichi(), False)

    def test_dont_call_riichi_expensive_damaten_with_yaku(self):
        self._make_table(dora_indicators=[
            self._string_to_136_tile(man='7'),
            self._string_to_136_tile(man='5'),
            self._string_to_136_tile(sou='1'),
        ])

        # tanyao pinfu sanshoku dora 4 - this is damaten baiman, let's not riichi it
        tiles = self._string_to_136_array(man='67888', sou='678', pin='34678')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), False)

        # let's test lots of doras hand, tanyao dora 8, also damaten baiman
        tiles = self._string_to_136_array(man='666888', sou='22', pin='34678')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), False)

        # chuuren
        tiles = self._string_to_136_array(man='1112345678999')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), False)

    def test_riichi_expensive_hand_without_yaku(self):
        self._make_table(dora_indicators=[
            self._string_to_136_tile(man='1'),
            self._string_to_136_tile(sou='1'),
            self._string_to_136_tile(pin='1')
        ])

        tiles = self._string_to_136_array(man='222', sou='22278', pin='22789')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), True)

    def test_riichi_tanki_honor_without_yaku(self):
        self._make_table(
            dora_indicators=[
                self._string_to_136_tile(man='2'),
                self._string_to_136_tile(sou='6')
            ]
        )

        tiles = self._string_to_136_array(man='345678', sou='789', pin='123', honors='2')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), True)

    def test_riichi_tanki_honor_chiitoitsu(self):
        self._make_table()

        tiles = self._string_to_136_array(man='22336688', sou='99', pin='99', honors='2')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), True)

    def test_always_call_daburi(self):
        self._make_table()
        self.player.round_step = 0

        tiles = self._string_to_136_array(sou='234567', pin='234567', man='4')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(man='5'))
        self.player.discard_tile()

        self.assertEqual(self.player.can_call_riichi(), True)

    def test_dont_call_karaten_tanki_riichi(self):
        self._make_table()

        tiles = self._string_to_136_array(man='22336688', sou='99', pin='99', honors='2')
        self.player.init_hand(tiles)

        for i in range(0, 3):
            self.table.add_discarded_tile(1, self._string_to_136_tile(honors='2'), False)
            self.table.add_discarded_tile(1, self._string_to_136_tile(honors='3'), False)

        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), False)

    def test_dont_call_karaten_ryanmen_riichi(self):
        self._make_table(dora_indicators=[
            self._string_to_136_tile(man='1'),
            self._string_to_136_tile(sou='1'),
            self._string_to_136_tile(pin='1')
        ])

        tiles = self._string_to_136_array(man='222', sou='22278', pin='22789')
        self.player.init_hand(tiles)

        for i in range(0, 4):
            self.table.add_discarded_tile(1, self._string_to_136_tile(sou='6'), False)
            self.table.add_discarded_tile(1, self._string_to_136_tile(sou='9'), False)

        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), False)

    def test_call_riichi_penchan_with_suji(self):
        self._make_table(dora_indicators=[
            self._string_to_136_tile(pin='1'),
        ])

        tiles = self._string_to_136_array(sou='11223', pin='234567', man='66')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(sou='6'))
        self.player.discard_tile()

        self.assertEqual(self.player.can_call_riichi(), True)

    def test_call_riichi_tanki_with_kabe(self):
        self._make_table(dora_indicators=[
            self._string_to_136_tile(pin='1'),
        ])

        for i in range(0, 3):
            self.table.add_discarded_tile(1, self._string_to_136_tile(honors='1'), False)

        for i in range(0, 4):
            self.table.add_discarded_tile(1, self._string_to_136_tile(sou='8'), False)

        tiles = self._string_to_136_array(sou='1119', pin='234567', man='666')
        self.player.init_hand(tiles)
        self.player.draw_tile(self._string_to_136_tile(honors='1'))
        self.player.discard_tile()

        self.assertEqual(self.player.can_call_riichi(), True)

    def test_call_riichi_chiitoitsu_with_suji(self):
        self._make_table(dora_indicators=[
            self._string_to_136_tile(man='1'),
        ])

        for i in range(0, 3):
            self.table.add_discarded_tile(1, self._string_to_136_tile(honors='3'), False)

        tiles = self._string_to_136_array(man='22336688', sou='9', pin='99', honors='22')
        self.player.init_hand(tiles)
        self.player.add_discarded_tile(Tile(self._string_to_136_tile(sou='6'), True))

        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), True)

    def test_dont_call_riichi_chiitoitsu_bad_wait(self):
        self._make_table(dora_indicators=[
            self._string_to_136_tile(man='1'),
        ])

        for i in range(0, 3):
            self.table.add_discarded_tile(1, self._string_to_136_tile(honors='3'), False)

        tiles = self._string_to_136_array(man='22336688', sou='4', pin='99', honors='22')
        self.player.init_hand(tiles)

        self.player.draw_tile(self._string_to_136_tile(honors='3'))
        self.player.discard_tile()
        self.assertEqual(self.player.can_call_riichi(), False)
