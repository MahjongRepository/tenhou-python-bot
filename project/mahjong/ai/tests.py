# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.agari import Agari
from mahjong.ai.main import MainAI, Defence
from mahjong.ai.shanten import Shanten
from mahjong.player import Player
from mahjong.table import Table
from mahjong.tile import TilesConverter


class AITestCase(unittest.TestCase):

    def test_outs(self):
        table = Table()
        player = Player(0, table)
        ai = MainAI(table, player)

        tiles = TilesConverter.string_to_136_array(sou='111345677', pin='15', man='56')
        tile = TilesConverter.string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        outs, shanten = ai.calculate_outs()

        self.assertEqual(shanten, 2)
        self.assertEqual(outs[0]['discard'], 26)
        self.assertEqual(outs[0]['waiting'], [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 21, 24])
        self.assertEqual(outs[0]['tiles_count'], 57)

        tiles = TilesConverter.string_to_136_array(sou='111345677', pin='45', man='56')
        tile = TilesConverter.string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        outs, shanten = ai.calculate_outs()

        self.assertEqual(shanten, 1)
        self.assertEqual(outs[0]['discard'], 26)
        self.assertEqual(outs[0]['waiting'], [11, 14, 21, 24])
        self.assertEqual(outs[0]['tiles_count'], 16)

        tiles = TilesConverter.string_to_136_array(sou='11145677', pin='345', man='56')
        tile = TilesConverter.string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        outs, shanten = ai.calculate_outs()

        self.assertEqual(shanten, 0)
        self.assertEqual(outs[0]['discard'], 26)
        self.assertEqual(outs[0]['waiting'], [21, 24])
        self.assertEqual(outs[0]['tiles_count'], 8)

        tiles = TilesConverter.string_to_136_array(sou='11145677', pin='345', man='56')
        tile = TilesConverter.string_to_136_array(man='4')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        outs, shanten = ai.calculate_outs()

        self.assertEqual(shanten, Shanten.AGARI_STATE)
        self.assertEqual(len(outs), 0)

    def test_discard_tile(self):
        table = Table()
        player = Player(0, table)

        tiles = TilesConverter.string_to_136_array(sou='111345677', pin='15', man='56')
        tile = TilesConverter.string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 104)

        player.draw_tile(TilesConverter.string_to_136_array(pin='4')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 36)

        player.draw_tile(TilesConverter.string_to_136_array(pin='3')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 20)

        player.draw_tile(TilesConverter.string_to_136_array(man='4')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, Shanten.AGARI_STATE)

    def test_discard_isolated_honor_tiles_first(self):
        table = Table()
        player = Player(0, table)

        tiles = TilesConverter.string_to_136_array(sou='8', pin='56688', man='11323', honors='36')
        tile = TilesConverter.string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 128)

        player.draw_tile(TilesConverter.string_to_136_array(man='4')[0])

        discarded_tile = player.discard_tile()
        self.assertEqual(discarded_tile, 116)

    def test_set_is_tempai_flag_to_the_player(self):
        table = Table()
        player = Player(0, table)

        tiles = TilesConverter.string_to_136_array(sou='111345677', pin='45', man='56')
        tile = TilesConverter.string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        player.discard_tile()
        self.assertEqual(player.in_tempai, False)

        tiles = TilesConverter.string_to_136_array(sou='11145677', pin='345', man='56')
        tile = TilesConverter.string_to_136_array(man='9')[0]
        player.init_hand(tiles)
        player.draw_tile(tile)

        player.discard_tile()
        self.assertEqual(player.in_tempai, True)


class AgariTestCase(unittest.TestCase):

    def test_is_agari(self):
        agari = Agari()

        tiles = TilesConverter.string_to_136_array(sou='123456789', pin='123', man='33')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='123456789', pin='11123')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='123456789', honors='11777')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='12345556778899')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='11123456788999')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='233334', pin='789', man='345', honors='55')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

    def test_is_not_agari(self):
        agari = Agari()

        tiles = TilesConverter.string_to_136_array(sou='123456789', pin='12345')
        self.assertFalse(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='111222444', pin='11145')
        self.assertFalse(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='11122233356888')
        self.assertFalse(agari.is_agari(TilesConverter.to_34_array(tiles)))

    def test_is_chitoitsu_agari(self):
        agari = Agari()

        tiles = TilesConverter.string_to_136_array(sou='1133557799', pin='1199')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='2244', pin='1199', man='11', honors='2277')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(man='11223344556677')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

    def test_is_kokushi_musou_agari(self):
        agari = Agari()

        tiles = TilesConverter.string_to_136_array(sou='19', pin='19', man='199', honors='1234567')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='19', pin='19', man='19', honors='11234567')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='19', pin='19', man='19', honors='12345677')
        self.assertTrue(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='129', pin='19', man='19', honors='1234567')
        self.assertFalse(agari.is_agari(TilesConverter.to_34_array(tiles)))

        tiles = TilesConverter.string_to_136_array(sou='19', pin='19', man='19', honors='11134567')
        self.assertFalse(agari.is_agari(TilesConverter.to_34_array(tiles)))


class ShantenTestCase(unittest.TestCase):

    def test_shanten_number(self):
        shanten = Shanten()

        tiles = TilesConverter.string_to_136_array(sou='111234567', pin='11', man='567')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), Shanten.AGARI_STATE)

        tiles = TilesConverter.string_to_136_array(sou='111345677', pin='11', man='567')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 0)

        tiles = TilesConverter.string_to_136_array(sou='111345677', pin='15', man='567')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 1)

        tiles = TilesConverter.string_to_136_array(sou='11134567', pin='15', man='1578')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 2)

        tiles = TilesConverter.string_to_136_array(sou='113456', pin='1358', man='1358')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 3)

        tiles = TilesConverter.string_to_136_array(sou='1589', pin='13588', man='1358', honors='1')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 4)

        tiles = TilesConverter.string_to_136_array(sou='159', pin='13588', man='1358', honors='12')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 5)

        tiles = TilesConverter.string_to_136_array(sou='1589', pin='258', man='1358', honors='123')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 6)

        tiles = TilesConverter.string_to_136_array(sou='11123456788999')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), Shanten.AGARI_STATE)

        tiles = TilesConverter.string_to_136_array(sou='11122245679999')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 0)

    def test_shanten_number_and_chitoitsu(self):
        shanten = Shanten()

        tiles = TilesConverter.string_to_136_array(sou='114477', pin='114477', man='77')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), Shanten.AGARI_STATE)

        tiles = TilesConverter.string_to_136_array(sou='114477', pin='114477', man='76')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 0)

        tiles = TilesConverter.string_to_136_array(sou='114477', pin='114479', man='76')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 1)

        tiles = TilesConverter.string_to_136_array(sou='114477', pin='14479', man='76', honors='1')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 2)

    def test_shanten_number_and_kokushi_musou(self):
        shanten = Shanten()

        tiles = TilesConverter.string_to_136_array(sou='19', pin='19', man='19', honors='12345677')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), Shanten.AGARI_STATE)

        tiles = TilesConverter.string_to_136_array(sou='129', pin='19', man='19', honors='1234567')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 0)

        tiles = TilesConverter.string_to_136_array(sou='129', pin='129', man='19', honors='123456')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 1)

        tiles = TilesConverter.string_to_136_array(sou='129', pin='129', man='129', honors='12345')
        self.assertEqual(shanten.calculate_shanten(TilesConverter.to_34_array(tiles)), 2)


class DefenceTestCase(unittest.TestCase):

    def test_go_to_the_defence_mode(self):
        table = Table()
        defence = Defence(table)

        self.assertFalse(defence.go_to_defence_mode())
        table.players[1].in_riichi = True
        self.assertTrue(defence.go_to_defence_mode())

        table.players[0].in_riichi = True
        self.assertFalse(defence.go_to_defence_mode())
