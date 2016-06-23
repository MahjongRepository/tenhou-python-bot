# -*- coding: utf-8 -*-
from random import randint, shuffle, random

from mahjong.ai.agari import Agari
from mahjong.client import Client
from mahjong.hand import FinishedHand
from mahjong.tile import TilesConverter

shuffle_seed = random

class GameManager(object):
    """
    Draft of bots runner.
    Is not completed yet
    """

    tiles = []
    dead_wall = []
    clients = []
    dora_indicators = []

    dealer = None
    current_client = None
    round_number = 0
    honba_sticks = 0
    riichi_sticks = 0

    _unique_dealers = 0


    def __init__(self, clients):
        self.tiles = []
        self.dead_wall = []
        self.dora_indicators = []
        self.clients = clients

        self.agari = Agari()

    def init_game(self):
        """
        Initial of the game.
        Clients random placement and dealer selection
        """
        shuffle(self.clients, shuffle_seed)

        dealer = randint(0, 3)
        self.set_dealer(dealer)

        for client in self.clients:
            # 250 is tenhou format, will be converted inside table class
            client.player.scores = 250

    def init_round(self):
        self._unique_dealers = 1
        self.tiles = [i for i in range(0, 136)]

        # need to change random function in future
        shuffle(self.tiles, shuffle_seed)

        self.dead_wall = self._cut_tiles(14)
        self.dora_indicators.append(self.dead_wall[8])

        player_scores = [i.player.scores for i in self.clients]

        for x in range(0, len(self.clients)):
            client = self.clients[x]

            # each client think that he is a player with position=0
            # so, we need to move dealer position for each client
            client_dealer = self.dealer - x

            client.table.init_round(
                self.round_number,
                self.honba_sticks,
                self.riichi_sticks,
                self.dora_indicators[0],
                client_dealer,
                player_scores
            )

        # each player by rotation draw 4 tiles until they have 12
        # after this each player draw one more tile
        # and this is will be their initial hand
        # we do it to make the tiles allocation in hands
        # more random
        for x in range(0, 3):
            for client in self.clients:
                client.player.tiles += self._cut_tiles(4)

        for client in self.clients:
            client.player.tiles += self._cut_tiles(1)
            client.init_hand(client.player.tiles)

    def play_round(self):
        continue_to_play = True

        while continue_to_play:
            client = self._get_current_client()

            tile, in_tempai, is_win = self.draw_tile(client)

            # win by tsumo after tile draw
            if is_win:
                result = self.process_the_end_of_the_round(client.player.tiles, client, None, True)
                return result

            tile = self.discard_tile(client)

            # after tile discard let's check all other players can they win or not
            # at this tile
            for other_client in self.clients:
                # there is no need to check the current client
                if other_client == client:
                    continue

                # TODO support multiple ron
                if self.can_call_ron(other_client, tile):
                    # the end of the round
                    result = self.process_the_end_of_the_round(other_client.player.tiles, other_client, client, False)
                    return result

            # if there is no challenger to ron, let's check can we call riichi with tile discard or not
            if in_tempai and client.player.can_call_riichi():
                self.call_riichi(client)

            self.current_client = self._move_position(self.current_client)

            # retake
            if not len(self.tiles):
                continue_to_play = False

        result = self.process_the_end_of_the_round(None, None, None, False)
        return result

    def draw_tile(self, client):
        tile = self._cut_tiles(1)[0]
        client.draw_tile(tile)

        in_tempai = client.player.in_tempai
        is_win = self.agari.is_agari(TilesConverter.to_34_array(client.player.tiles))

        return tile, in_tempai, is_win

    def discard_tile(self, client):
        tile = client.discard_tile()
        return tile

    def can_call_ron(self, client, win_tile):
        if not client.player.in_tempai or not client.player.in_riichi:
            return False
        tiles = client.player.tiles
        is_ron = self.agari.is_agari(TilesConverter.to_34_array(tiles + [win_tile]))
        return is_ron

    def call_riichi(self, client):
        client.player.in_riichi = True
        client.player.scores -= 1000
        self.riichi_sticks += 1

    def set_dealer(self, dealer):
        self.dealer = dealer
        self._unique_dealers += 1

        for client in self.clients:
            client.player.is_dealer = False

        self.clients[dealer].player.is_dealer = True

        # first move should be dealer's move
        self.current_client = dealer

    def process_the_end_of_the_round(self, win_tiles, win_client, lose_client, is_tsumo):
        """
        Increment a round number and do a scores calculations
        """
        is_game_end = False
        self.round_number += 1

        hand_value = 0

        if win_client:
            hand_value += FinishedHand.estimate_hand_value(win_tiles,
                                                           is_tsumo,
                                                           win_client.player.in_riichi,
                                                           False)

            scores_to_pay = hand_value + self.riichi_sticks * 1000 + self.honba_sticks * 300
            self.riichi_sticks = 0
            # if dealer won we need to increment honba sticks
            if win_client.player.is_dealer:
                self.honba_sticks += 1
            else:
                self.honba_sticks = 0
                new_dealer = self._move_position(self.dealer)
                self.set_dealer(new_dealer)

            # win by ron
            if lose_client:
                win_client.player.scores += scores_to_pay
                lose_client.player.scores -= scores_to_pay
            # win by tsumo
            else:
                scores_to_pay /= 3
                # will be changed when real hand calculation will be implemented
                # round to nearest 100. 333 -> 300
                scores_to_pay = 100 * round(float(scores_to_pay) / 100)

                win_client.player.scores += scores_to_pay * 3
                for client in self.clients:
                    if client != win_client:
                        client.player.scores -= scores_to_pay
        # retake
        else:
            tempai_users = 0

            for client in self.clients:
                if client.player.in_tempai:
                    tempai_users += 1

            if tempai_users == 0:
                # no one in tempai, so honba stick should be added
                self.honba_sticks += 1
                new_dealer = self._move_position(self.dealer)
                self.set_dealer(new_dealer)
            else:
                # 1 tempai user  will get 3000
                # 2 tempai users will get 1500 each
                # 3 tempai users will get 1000 each
                scores_reward = 3000 / tempai_users
                for client in self.clients:
                    if client.player.in_tempai:
                        client.player.scores += scores_reward

                        # dealer was tempai, we need to add honba stick
                        if client.player.is_dealer:
                            self.honba_sticks += 1
                    else:
                        client.player.scores -= 3000 / (4 - tempai_users)

        # if someone has negative scores,
        # we need to end the game
        for client in self.clients:
            if client.player.scores < 0:
                is_game_end = True

        # we have played all 8 winds, let's finish the game
        if self._unique_dealers > 8:
            is_game_end = True

        return {
            'win_hand': win_tiles,
            'win_client': win_client,
            'lose_client': lose_client,
            'is_tsumo': is_tsumo,
            'is_game_end': is_game_end
        }

    def _get_current_client(self) -> Client:
        return self.clients[self.current_client]

    def _cut_tiles(self, count_of_tiles) -> []:
        """
        Cut the tiles array
        :param count_of_tiles: how much tiles to cut
        :return: the array with specified count of tiles
        """

        result = self.tiles[0:count_of_tiles]
        self.tiles = self.tiles[count_of_tiles:len(self.tiles)]
        return result

    def _move_position(self, current_position):
        """
        loop 0 -> 1 -> 2 -> 3 -> 0
        """
        current_position += 1
        if current_position > 3:
            current_position = 0
        return current_position
