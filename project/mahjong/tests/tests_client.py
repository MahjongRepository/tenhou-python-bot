# -*- coding: utf-8 -*-
import unittest

from mahjong.client import Client
from mahjong.meld import Meld


class ClientTestCase(unittest.TestCase):

    def test_draw_tile(self):
        client = Client()
        tiles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])
        client.table.init_main_player_hand(tiles)
        self.assertEqual(len(client.table.get_main_player().tiles), 13)
        self.assertEqual(client.table.count_of_remaining_tiles, 70)

        client.draw_tile(14)

        self.assertEqual(len(client.table.get_main_player().tiles), 14)
        self.assertEqual(client.table.count_of_remaining_tiles, 69)

    def test_discard_tile(self):
        client = Client()
        tiles = [1, 22, 3, 4, 43, 6, 7, 8, 9, 55, 11, 12, 13, 99]
        client.table.init_main_player_hand(tiles)
        self.assertEqual(len(client.table.get_main_player().tiles), 14)

        tile = client.discard_tile()

        self.assertEqual(len(client.table.get_main_player().tiles), 13)
        self.assertEqual(len(client.table.get_main_player().discards), 1)
        self.assertFalse(tile in client.table.get_main_player().tiles)

    def test_call_meld(self):
        client = Client()

        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])
        self.assertEqual(client.table.count_of_remaining_tiles, 70)

        meld = Meld()

        client.add_called_meld(meld)

        self.assertEqual(len(client.player.melds), 1)
        self.assertEqual(client.table.count_of_remaining_tiles, 71)

    def test_enemy_discard(self):
        client = Client()
        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])

        self.assertEqual(client.table.count_of_remaining_tiles, 70)

        client.enemy_discard(10, 1)

        self.assertEqual(len(client.table.get_player(1).discards), 1)
        self.assertEqual(client.table.count_of_remaining_tiles, 69)

    def test_enemy_discard_and_safe_tiles(self):
        client = Client()
        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])

        client.table.players[0].in_riichi = True
        client.enemy_discard(10, 1)

        self.assertEqual(len(client.table.players[0].safe_tiles), 1)

    def test_enemy_in_riichi(self):
        client = Client()
        client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])
        player_seat = 1

        self.assertEqual(client.table.get_player(player_seat).in_riichi, False)

        client.enemy_riichi(player_seat)

        self.assertEqual(client.table.get_player(player_seat).in_riichi, True)
