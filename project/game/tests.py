# -*- coding: utf-8 -*-
import logging
import unittest

import game.game_manager
from game.game_manager import GameManager
from mahjong.client import Client
from utils.tests import TestMixin


class GameManagerTestCase(unittest.TestCase, TestMixin):

    def setUp(self):
        logger = logging.getLogger('game')
        logger.disabled = False

    # def test_debug(self):
    #     game.game_manager.shuffle_seed = lambda: 0.4504654144106681
    #
    #     clients = [Client(use_previous_ai_version=False) for _ in range(0, 4)]
    #     # clients = [Client(use_previous_ai_version=True) for _ in range(0, 3)]
    #     # clients += [Client(use_previous_ai_version=False)]
    #     manager = GameManager(clients)
    #     manager.init_game()
    #     manager.set_dealer(3)
    #     manager._unique_dealers = 4
    #     manager.init_round()
    #
    #     result = manager.play_round()

    def test_init_game(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()

        self.assertTrue(manager.dealer in [0, 1, 2, 3])

    def test_init_round(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        self.assertEqual(len(manager.dead_wall), 14)
        self.assertEqual(len(manager.dora_indicators), 1)
        self.assertIsNotNone(manager.current_client_seat)
        self.assertEqual(manager.round_number, 0)
        self.assertEqual(manager.honba_sticks, 0)
        self.assertEqual(manager.riichi_sticks, 0)
        self.assertEqual([i.player.scores for i in manager.clients], [25000, 25000, 25000, 25000])

        for client in clients:
            self.assertEqual(len(client.player.tiles), 13)

        self.assertEqual(len(manager.tiles), 70)

    def test_init_dealer(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.set_dealer(0)
        manager.init_round()

        self.assertTrue(manager.clients[0].player.is_dealer)
        self.assertFalse(manager.clients[1].player.is_dealer)
        self.assertFalse(manager.clients[2].player.is_dealer)
        self.assertFalse(manager.clients[3].player.is_dealer)

        manager.set_dealer(1)
        manager.init_round()

        self.assertTrue(manager.clients[1].player.is_dealer)
        self.assertFalse(manager.clients[0].player.is_dealer)
        self.assertFalse(manager.clients[2].player.is_dealer)
        self.assertFalse(manager.clients[3].player.is_dealer)

        manager.set_dealer(2)
        manager.init_round()

        self.assertTrue(manager.clients[2].player.is_dealer)
        self.assertFalse(manager.clients[0].player.is_dealer)
        self.assertFalse(manager.clients[1].player.is_dealer)
        self.assertFalse(manager.clients[3].player.is_dealer)

        manager.set_dealer(3)
        manager.init_round()

        self.assertTrue(manager.clients[3].player.is_dealer)
        self.assertFalse(manager.clients[0].player.is_dealer)
        self.assertFalse(manager.clients[1].player.is_dealer)
        self.assertFalse(manager.clients[2].player.is_dealer)

    def test_init_scores_and_recalculate_position(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(3)

        clients[0].player.scores = 24000
        clients[1].player.scores = 23000
        clients[2].player.scores = 22000
        clients[3].player.scores = 21000

        manager.recalculate_players_position()

        self.assertEqual(clients[0].player.scores, 24000)
        self.assertEqual(clients[0].player.position, 1)
        self.assertEqual(clients[1].player.scores, 23000)
        self.assertEqual(clients[1].player.position, 2)
        self.assertEqual(clients[2].player.scores, 22000)
        self.assertEqual(clients[2].player.position, 3)
        self.assertEqual(clients[3].player.scores, 21000)
        self.assertEqual(clients[3].player.position, 4)

        clients[0].player.scores = 24000
        clients[1].player.scores = 24000
        clients[2].player.scores = 22000
        clients[3].player.scores = 22000

        manager.recalculate_players_position()

        self.assertEqual(clients[0].player.scores, 24000)
        self.assertEqual(clients[0].player.position, 1)
        self.assertEqual(clients[1].player.scores, 24000)
        self.assertEqual(clients[1].player.position, 2)
        self.assertEqual(clients[2].player.scores, 22000)
        self.assertEqual(clients[2].player.position, 3)
        self.assertEqual(clients[3].player.scores, 22000)
        self.assertEqual(clients[3].player.position, 4)

    def test_call_riichi(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        client = clients[0]
        self.assertEqual(manager.riichi_sticks, 0)
        self.assertEqual(client.player.scores, 25000)
        self.assertEqual(client.player.in_riichi, False)

        manager.call_riichi(client)

        self.assertEqual(manager.riichi_sticks, 1)
        self.assertEqual(client.player.scores, 24000)
        self.assertEqual(client.player.in_riichi, True)

        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        manager.call_riichi(clients[0])

        self.assertEqual(clients[0].player.in_riichi, True)
        self.assertEqual(clients[1].player.in_riichi, False)
        self.assertEqual(clients[2].player.in_riichi, False)
        self.assertEqual(clients[3].player.in_riichi, False)

        for client in clients:
            client.player.in_riichi = False

        manager.call_riichi(clients[1])

        self.assertEqual(clients[0].player.in_riichi, False)
        self.assertEqual(clients[1].player.in_riichi, True)
        self.assertEqual(clients[2].player.in_riichi, False)
        self.assertEqual(clients[3].player.in_riichi, False)

        for client in clients:
            client.player.in_riichi = False

        manager.call_riichi(clients[2])

        self.assertEqual(clients[0].player.in_riichi, False)
        self.assertEqual(clients[1].player.in_riichi, False)
        self.assertEqual(clients[2].player.in_riichi, True)
        self.assertEqual(clients[3].player.in_riichi, False)

        for client in clients:
            client.player.in_riichi = False

        manager.call_riichi(clients[3])

        self.assertEqual(clients[0].player.in_riichi, False)
        self.assertEqual(clients[1].player.in_riichi, False)
        self.assertEqual(clients[2].player.in_riichi, False)
        self.assertEqual(clients[3].player.in_riichi, True)

    def test_play_round_and_win_by_tsumo(self):
        game.game_manager.shuffle_seed = lambda: 0.6718028503751606

        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(3)
        manager.init_round()

        result = manager.play_round()

        self.assertEqual(manager.round_number, 1)
        self.assertEqual(result['is_tsumo'], True)
        self.assertEqual(result['is_game_end'], False)
        self.assertNotEqual(result['winner'], None)
        self.assertEqual(result['loser'], None)

    def test_play_round_and_win_by_ron(self):
        game.game_manager.shuffle_seed = lambda: 0.33

        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(3)
        manager.init_round()

        result = manager.play_round()

        self.assertEqual(manager.round_number, 1)
        self.assertEqual(result['is_tsumo'], False)
        self.assertEqual(result['is_game_end'], False)
        self.assertNotEqual(result['winner'], None)
        self.assertNotEqual(result['loser'], None)

    def test_play_round_with_retake(self):
        game.game_manager.shuffle_seed = lambda: 0.5859797343777

        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(3)
        manager.init_round()

        result = manager.play_round()

        self.assertEqual(manager.round_number, 1)
        self.assertEqual(result['is_tsumo'], False)
        self.assertEqual(result['is_game_end'], False)
        self.assertEqual(result['winner'], None)
        self.assertEqual(result['loser'], None)

    def test_play_round_and_open_yakuhai_hand(self):
        game.game_manager.shuffle_seed = lambda: 0.457500580104948

        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(3)
        manager.init_round()

        result = manager.play_round()

        self.assertEqual(len(result['players_with_open_hands']), 2)

    def test_scores_calculations_after_retake(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 25000)
        self.assertEqual(clients[1].player.scores, 25000)
        self.assertEqual(clients[2].player.scores, 25000)
        self.assertEqual(clients[3].player.scores, 25000)

        clients[0].player.in_tempai = True
        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 28000)
        self.assertEqual(clients[1].player.scores, 24000)
        self.assertEqual(clients[2].player.scores, 24000)
        self.assertEqual(clients[3].player.scores, 24000)

        for client in clients:
            client.player.scores = 25000

        clients[0].player.in_tempai = True
        clients[1].player.in_tempai = True
        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 26500)
        self.assertEqual(clients[1].player.scores, 26500)
        self.assertEqual(clients[2].player.scores, 23500)
        self.assertEqual(clients[3].player.scores, 23500)

        for client in clients:
            client.player.scores = 25000

        clients[0].player.in_tempai = True
        clients[1].player.in_tempai = True
        clients[2].player.in_tempai = True
        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 26000)
        self.assertEqual(clients[1].player.scores, 26000)
        self.assertEqual(clients[2].player.scores, 26000)
        self.assertEqual(clients[3].player.scores, 22000)

        for client in clients:
            client.player.scores = 25000

        clients[0].player.in_tempai = True
        clients[1].player.in_tempai = True
        clients[2].player.in_tempai = True
        clients[3].player.in_tempai = True
        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 25000)
        self.assertEqual(clients[1].player.scores, 25000)
        self.assertEqual(clients[2].player.scores, 25000)
        self.assertEqual(clients[3].player.scores, 25000)

    def test_retake_and_honba_increment(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        # no one in tempai, so honba stick should be added
        manager.process_the_end_of_the_round([], None, None, None, False)
        self.assertEqual(manager.honba_sticks, 1)

        manager.honba_sticks = 0
        manager.set_dealer(0)
        clients[0].player.in_tempai = False
        clients[1].player.in_tempai = True

        # dealer NOT in tempai, no honba
        manager.process_the_end_of_the_round([], None, None, None, False)
        self.assertEqual(manager.honba_sticks, 0)

        clients[0].player.in_tempai = True

        # dealer in tempai, so honba stick should be added
        manager.process_the_end_of_the_round([], None, None, None, False)
        self.assertEqual(manager.honba_sticks, 1)

    def test_win_by_ron_and_scores_calculation(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()
        manager.set_dealer(0)

        winner = clients[0]
        loser = clients[1]

        # only 1500 hand
        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, loser, False)
        self.assertEqual(winner.player.scores, 26500)
        self.assertEqual(loser.player.scores, 23500)

        winner.player.scores = 25000
        winner.player.dealer_seat = 1
        loser.player.scores = 25000
        manager.riichi_sticks = 2
        manager.honba_sticks = 2

        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, loser, False)
        self.assertEqual(winner.player.scores, 28600)
        self.assertEqual(loser.player.scores, 23400)
        self.assertEqual(manager.riichi_sticks, 0)
        self.assertEqual(manager.honba_sticks, 0)

        winner.player.scores = 25000
        winner.player.dealer_seat = 0
        loser.player.scores = 25000
        manager.honba_sticks = 2

        # if dealer won we need to increment honba sticks
        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, loser, False)
        self.assertEqual(winner.player.scores, 27100)
        self.assertEqual(loser.player.scores, 22900)
        self.assertEqual(manager.honba_sticks, 3)

    def test_win_by_tsumo_and_scores_calculation(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()
        manager.riichi_sticks = 1
        manager.honba_sticks = 1

        winner = clients[0]
        manager.set_dealer(0)
        manager.dora_indicators = [100]
        # to avoid ura-dora, because of this test can fail
        winner.player.in_riichi = False

        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, None, True)

        # 2400 + riichi stick (1000) = 3400
        # 700 from each other player + 100 honba payment
        self.assertEqual(winner.player.scores, 28400)
        self.assertEqual(clients[1].player.scores, 24200)
        self.assertEqual(clients[2].player.scores, 24200)
        self.assertEqual(clients[3].player.scores, 24200)

        for client in clients:
            client.player.scores = 25000

        winner = clients[0]
        manager.set_dealer(1)
        winner.player.in_riichi = False
        manager.riichi_sticks = 0
        manager.honba_sticks = 0

        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, None, True)

        # 700 from dealer and 400 from other players
        self.assertEqual(winner.player.scores, 26500)
        self.assertEqual(clients[1].player.scores, 24600)
        self.assertEqual(clients[2].player.scores, 24300)
        self.assertEqual(clients[3].player.scores, 24600)

    def test_change_dealer_after_end_of_the_round(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.set_dealer(0)
        manager.init_round()

        # retake. dealer is NOT in tempai, let's move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), None, None, None, False)
        self.assertEqual(manager.dealer, 1)

        # retake. dealer is in tempai, don't move a dealer position
        clients[1].player.in_tempai = True
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, None, None, False)
        self.assertEqual(manager.dealer, 1)

        # dealer win by ron, don't move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, None, None, False)
        self.assertEqual(manager.dealer, 1)

        # dealer win by tsumo, don't move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, None, None, False)
        self.assertEqual(manager.dealer, 1)

        # NOT dealer win by ron, let's move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, clients[3], clients[2], False)
        self.assertEqual(manager.dealer, 2)

        # NOT dealer win by tsumo, let's move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, clients[1], None, True)
        self.assertEqual(manager.dealer, 3)

    def test_is_game_end_by_negative_scores(self):
        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.set_dealer(0)
        manager.init_round()

        winner = clients[0]
        loser = clients[1]
        manager.dora_indicators = [100]
        loser.player.scores = 0

        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        result = manager.process_the_end_of_the_round(tiles, win_tile, winner, loser, False)
        self.assertEqual(loser.player.scores, -1500)
        self.assertEqual(result['is_game_end'], True)

    def test_is_game_end_by_eight_winds(self):
        clients = [Client() for _ in range(0, 4)]

        current_dealer = 0
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(current_dealer)
        manager.init_round()
        manager._unique_dealers = 1

        for x in range(0, 7):
            # to avoid honba
            result = manager.process_the_end_of_the_round([], 0, None, None, True)
            self.assertEqual(result['is_game_end'], False)
            self.assertNotEqual(manager.dealer, current_dealer)
            current_dealer = manager.dealer

        result = manager.process_the_end_of_the_round(list(range(0, 13)), 0, clients[0], None, True)
        self.assertEqual(result['is_game_end'], True)

    def test_ron_with_not_correct_hand(self):
        """
        With open for yakuhai strategy we can have situation like this
        234567m67s66z + 8s + [444z]
        We have open hand and we don't have yaku in the hand
        In that case we can't call ron.
        Round should be ended without exceptions
        """
        game.game_manager.shuffle_seed = lambda: 0.5082102963203375

        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(1)
        manager.init_round()

        manager.play_round()

    def test_tsumo_with_not_correct_hand(self):
        """
        With open for yakuhai strategy we can have situation like this
        234567m67s66z + 8s + [444z]
        We have open hand and we don't have yaku in the hand
        In that case we can't call tsumo.
        Round should be ended without exceptions
        """
        game.game_manager.shuffle_seed = lambda: 0.26483054978923926

        clients = [Client() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(1)
        manager.init_round()

        manager.play_round()
