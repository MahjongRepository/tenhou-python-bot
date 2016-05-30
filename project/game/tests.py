# -*- coding: utf-8 -*-
import unittest

import game.game_manager
from game.game_manager import GameManager
from mahjong.client import Client
from mahjong.player import Player
from mahjong.table import Table


class TenhouDecoderTestCase(unittest.TestCase):

    def test_init_round(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_round()

        self.assertEqual(len(manager.dead_wall), 14)
        self.assertEqual(len(manager.dora_indicators), 1)
        self.assertIsNotNone(manager.dealer)
        self.assertIsNotNone(manager.current_client)
        self.assertEqual(manager.round_number, 0)
        self.assertEqual(manager.honba_sticks, 0)
        self.assertEqual(manager.riichi_sticks, 0)
        self.assertEqual([i.player.scores for i in manager.clients], [25000, 25000, 25000, 25000])

        for client in clients:
            self.assertEqual(len(client.player.tiles), 13)

        self.assertEqual(len(manager.tiles), 70)

    def test_call_riichi(self):
        game.game_manager.shuffle_seed = lambda : 0.33

        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_round()

        client = clients[0]
        self.assertEqual(manager.riichi_sticks, 0)
        self.assertEqual(client.player.scores, 25000)
        self.assertEqual(client.player.in_riichi, False)

        manager.call_riichi(client)

        self.assertEqual(manager.riichi_sticks, 1)
        self.assertEqual(client.player.scores, 24000)
        self.assertEqual(client.player.in_riichi, True)

    def test_play_round(self):
        game.game_manager.shuffle_seed = lambda : 0.33

        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_round()
        manager.dealer = 3

        manager = GameManager(clients)
        manager.init_round()

        manager.play_round()

        self.assertEqual(manager.round_number, 1)

