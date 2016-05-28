# -*- coding: utf-8 -*-
import unittest

import game.game_manager
from game.game_manager import GameManager
from mahjong.player import Player
from mahjong.table import Table


class TenhouDecoderTestCase(unittest.TestCase):

    def test_init_round(self):
        table = Table()
        players = [Player(i, table) for i in range(0, 4)]

        manager = GameManager(players)
        manager.init_round()

        self.assertEqual(len(manager.dead_wall), 14)
        self.assertEqual(len(manager.dora_indicators), 1)
        self.assertIsNotNone(manager.dealer)
        self.assertIsNotNone(manager.current_player)
        self.assertEqual(manager.round_number, 0)
        self.assertEqual(manager.honba_sticks, 0)
        self.assertEqual(manager.riichi_sticks, 0)
        self.assertEqual(manager.player_scores, [25000, 25000, 25000, 25000])

        for player in players:
            self.assertEqual(len(player.tiles), 13)

        self.assertEqual(len(manager.tiles), 70)

    def test_draw_and_discard_tile(self):
        table = Table()
        players = [Player(i, table) for i in range(0, 4)]

        manager = GameManager(players)
        manager.init_round()

        manager.dealer = 0
        manager.current_player = 0

        manager.draw_tile()
        manager.discard_tile()
        self.assertEqual(manager.current_player, 1)

        manager.draw_tile()
        manager.discard_tile()
        self.assertEqual(manager.current_player, 2)

        manager.draw_tile()
        manager.discard_tile()
        self.assertEqual(manager.current_player, 3)

        manager.draw_tile()
        manager.discard_tile()
        self.assertEqual(manager.current_player, 0)

    # def test_play_round(self):
    #     game.game_manager.seed = lambda : 0.33
    #
    #     table = Table()
    #     players = [Player(i, table) for i in range(0, 4)]
    #
    #     manager = GameManager(players)
    #     manager.init_round()
    #
    #     manager.play_round()
    #
    #     self.assertEqual(manager.round_number, 1)

