# -*- coding: utf-8 -*-
import unittest

from mahjong.ai.shanten import Shanten
from mahjong.tile import TilesConverter


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
