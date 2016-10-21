# -*- coding: utf-8 -*-
import logging
from collections import deque

from random import randint, shuffle, random

from game.logger import set_up_logging
from mahjong.ai.agari import Agari
from mahjong.client import Client
from mahjong.hand import FinishedHand
from mahjong.tile import TilesConverter

# we need to have it
# to be able repeat our tests with needed random
seed_value = random()

set_up_logging()
logger = logging.getLogger('game')


def shuffle_seed():
    return seed_value


class GameManager(object):
    """
    Allow to play bots between each other
    To have a metrics how new version plays agains old versions
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
        self._set_client_names()

        self.agari = Agari()
        self.finished_hand = FinishedHand()

    def init_game(self):
        """
        Initial of the game.
        Clients random placement and dealer selection
        """
        shuffle(self.clients, shuffle_seed)
        for i in range(0, len(self.clients)):
            self.clients[i].position = i

        dealer = randint(0, 3)
        self.set_dealer(dealer)

        for client in self.clients:
            client.player.scores = 25000

        self._unique_dealers = 1

    def init_round(self):
        # each round should have personal seed
        global seed_value
        seed_value = random()

        self.tiles = [i for i in range(0, 136)]

        # need to change random function in future
        shuffle(self.tiles, shuffle_seed)

        self.dead_wall = self._cut_tiles(14)
        self.dora_indicators.append(self.dead_wall[8])

        for x in range(0, len(self.clients)):
            client = self.clients[x]

            # each client think that he is a player with position = 0
            # so, we need to move dealer position for each client
            # and shift scores array
            client_dealer = self.dealer - x

            player_scores = deque([i.player.scores / 100 for i in self.clients])
            player_scores.rotate(x * -1)
            player_scores = list(player_scores)

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

        logger.info('Seed: {0}'.format(shuffle_seed()))
        logger.info('Dealer: {0}'.format(self.dealer))
        logger.info('Wind: {0}. Riichi sticks: {1}. Honba sticks: {2}'.format(
            self._unique_dealers,
            self.riichi_sticks,
            self.honba_sticks
        ))
        logger.info('Players: {0}'.format(self.players_sorted_by_scores()))

    def play_round(self):
        continue_to_play = True

        while continue_to_play:
            client = self._get_current_client()
            in_tempai = client.player.in_tempai

            tile = self._cut_tiles(1)[0]

            # we don't need to add tile to the hand when we are in riichi
            if client.player.in_riichi:
                tiles = client.player.tiles + [tile]
            else:
                client.draw_tile(tile)
                tiles = client.player.tiles

            is_win = self.agari.is_agari(TilesConverter.to_34_array(tiles))

            # win by tsumo after tile draw
            if is_win:
                result = self.process_the_end_of_the_round(tiles=client.player.tiles,
                                                           win_tile=tile,
                                                           winner=client,
                                                           loser=None,
                                                           is_tsumo=True)
                return result

            # if not in riichi, let's decide what tile to discard
            if not client.player.in_riichi:
                tile = client.discard_tile()
                in_tempai = client.player.in_tempai

            # after tile discard let's check all other players can they win or not
            # at this tile
            for other_client in self.clients:
                # there is no need to check the current client
                if other_client == client:
                    continue

                # let's store other players discards
                other_client.enemy_discard(other_client.position - client.position, tile)

                # TODO support multiple ron
                if self.can_call_ron(other_client, tile):
                    # the end of the round
                    result = self.process_the_end_of_the_round(tiles=other_client.player.tiles,
                                                               win_tile=tile,
                                                               winner=other_client,
                                                               loser=client,
                                                               is_tsumo=False)
                    return result

            # if there is no challenger to ron, let's check can we call riichi with tile discard or not
            if in_tempai and client.player.can_call_riichi():
                self.call_riichi(client)

            self.current_client = self._move_position(self.current_client)

            # retake
            if not len(self.tiles):
                continue_to_play = False

        result = self.process_the_end_of_the_round([], 0, None, None, False)
        return result

    def play_game(self, total_results):
        """
        :param total_results: a dictionary with keys as client ids
        :return: game results
        """
        logger.info('The start of the game')
        logger.info('')

        is_game_end = False
        self.init_game()

        played_rounds = 0

        while not is_game_end:
            self.init_round()
            result = self.play_round()

            is_game_end = result['is_game_end']
            loser = result['loser']
            winner = result['winner']
            if loser:
                total_results[loser.id]['lose_rounds'] += 1
            if winner:
                total_results[winner.id]['win_rounds'] += 1

            for client in self.clients:
                if client.player.in_riichi:
                    total_results[client.id]['riichi_rounds'] += 1

            played_rounds += 1

        self.recalculate_players_position()

        logger.info('Final Scores: {0}'.format(self.players_sorted_by_scores()))
        logger.info('The end of the game')

        return {'played_rounds': played_rounds}

    def recalculate_players_position(self):
        """
        For players with same count of scores we need
        to set position based on their initial seat on the table
        """
        temp_clients = sorted(self.clients, key=lambda x: x.player.scores, reverse=True)
        for i in range(0, len(temp_clients)):
            temp_client = temp_clients[i]

            for client in self.clients:
                if client.id == temp_client.id:
                    client.player.position = i + 1

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

        who_called_riichi = client.position
        for client in self.clients:
            client.enemy_riichi(who_called_riichi - client.position)

        logger.info('Riichi: {0} - 1,000'.format(client.player.name))

    def set_dealer(self, dealer):
        self.dealer = dealer
        self._unique_dealers += 1

        for client in self.clients:
            client.player.is_dealer = False

        self.clients[dealer].player.is_dealer = True

        # first move should be dealer's move
        self.current_client = dealer

    def process_the_end_of_the_round(self, tiles, win_tile, winner, loser, is_tsumo):
        """
        Increment a round number and do a scores calculations
        """

        if winner:
            logger.info('{0}: {1} + {2}'.format(
                is_tsumo and 'Tsumo' or 'Ron',
                TilesConverter.to_one_line_string(tiles),
                TilesConverter.to_one_line_string([win_tile])),
            )
        else:
            logger.info('Retake')

        is_game_end = False
        self.round_number += 1

        if winner:
            hand_value = self.finished_hand.estimate_hand_value(tiles + [win_tile],
                                                                win_tile,
                                                                is_tsumo,
                                                                winner.player.in_riichi,
                                                                winner.player.is_dealer,
                                                                False)
            if hand_value['cost']:
                hand_value = hand_value['cost']['main']
            else:
                logger.error('Can\'t estimate a hand: {0}. Error: {1}'.format(
                    TilesConverter.to_one_line_string(tiles + [win_tile]),
                    hand_value['error']
                ))
                hand_value = 1000

            scores_to_pay = hand_value + self.honba_sticks * 300
            riichi_bonus = self.riichi_sticks * 1000
            self.riichi_sticks = 0

            # if dealer won we need to increment honba sticks
            if winner.player.is_dealer:
                self.honba_sticks += 1
            else:
                self.honba_sticks = 0
                new_dealer = self._move_position(self.dealer)
                self.set_dealer(new_dealer)

            # win by ron
            if loser:
                win_amount = scores_to_pay + riichi_bonus
                winner.player.scores += win_amount
                loser.player.scores -= scores_to_pay

                logger.info('Win:  {0} + {1:,d}'.format(winner.player.name, win_amount))
                logger.info('Lose: {0} - {1:,d}'.format(loser.player.name, scores_to_pay))
            # win by tsumo
            else:
                scores_to_pay /= 3
                # will be changed when real hand calculation will be implemented
                # round to nearest 100. 333 -> 300
                scores_to_pay = 100 * round(float(scores_to_pay) / 100)

                win_amount = scores_to_pay * 3 + riichi_bonus
                winner.player.scores += win_amount

                for client in self.clients:
                    if client != winner:
                        client.player.scores -= scores_to_pay

                logger.info('Win: {0} + {1:,d}'.format(winner.player.name, win_amount))
        # retake
        else:
            tempai_users = 0

            for client in self.clients:
                if client.player.in_tempai:
                    tempai_users += 1

            if tempai_users == 0 or tempai_users == 4:
                self.honba_sticks += 1
                # no one in tempai, so deal should move
                if tempai_users == 0:
                    new_dealer = self._move_position(self.dealer)
                    self.set_dealer(new_dealer)
            else:
                # 1 tempai user  will get 3000
                # 2 tempai users will get 1500 each
                # 3 tempai users will get 1000 each
                scores_to_pay = 3000 / tempai_users
                for client in self.clients:
                    if client.player.in_tempai:
                        client.player.scores += scores_to_pay
                        logger.info('{0} + {1:,d}'.format(client.player.name, int(scores_to_pay)))

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

        logger.info('')

        return {
            'winner': winner,
            'loser': loser,
            'is_tsumo': is_tsumo,
            'is_game_end': is_game_end
        }

    def players_sorted_by_scores(self):
        return sorted([i.player for i in self.clients], key=lambda x: x.scores, reverse=True)

    def _set_client_names(self):
        """
        For better tests output
        """
        names = ['Sato', 'Suzuki', 'Takahashi', 'Tanaka', 'Watanabe', 'Ito',
                 'Yamamoto', 'Nakamura', 'Kobayashi', 'Kato', 'Yoshida', 'Yamada']

        for client in self.clients:
            name = names[randint(0, len(names) - 1)]
            names.remove(name)

            client.player.name = name

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
