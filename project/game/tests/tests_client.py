# -*- coding: utf-8 -*-
import unittest

from mahjong.meld import Meld

from game.client import Client


class ClientTestCase(unittest.TestCase):

    def test_discard_tile(self):
        client = Client()

        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])
        tiles = [1, 22, 3, 4, 43, 6, 7, 8, 9, 55, 11, 12, 13, 99]
        client.table.player.init_hand(tiles)

        self.assertEqual(len(client.table.player.tiles), 14)
        self.assertEqual(client.table.count_of_remaining_tiles, 70)

        tile = client.player.discard_tile()

        self.assertEqual(len(client.table.player.tiles), 13)
        self.assertEqual(len(client.table.player.discards), 1)
        self.assertFalse(tile in client.table.player.tiles)
        self.assertEqual(client.table.count_of_remaining_tiles, 69)

    def test_call_meld(self):
        client = Client()

        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])
        self.assertEqual(client.table.count_of_remaining_tiles, 70)

        meld = Meld()
        client.table.add_called_meld(0, meld)

        self.assertEqual(len(client.player.melds), 1)
        self.assertEqual(client.table.count_of_remaining_tiles, 71)

        client.player.tiles = [0]
        meld = Meld()
        meld.type = Meld.KAN
        meld.called_tile = 0
        client.table.add_called_meld(0, meld)

        self.assertEqual(len(client.player.melds), 2)
        # +1 for called meld
        # -1 for called kan
        self.assertEqual(client.table.count_of_remaining_tiles, 71)

    def test_enemy_discard(self):
        client = Client()
        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])

        self.assertEqual(client.table.count_of_remaining_tiles, 70)

        client.table.add_discarded_tile(1, 10, False)

        self.assertEqual(client.table.count_of_remaining_tiles, 69)
