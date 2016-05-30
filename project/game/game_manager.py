# -*- coding: utf-8 -*-
import logging

from random import randint, shuffle, random

from game.logger import set_up_logging
from mahjong.ai.agari import Agari
from mahjong.client import Client
from mahjong.tile import TilesConverter

shuffle_seed = random

set_up_logging()
logger = logging.getLogger('game')


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


    def __init__(self, clients):
        self.tiles = []
        self.dead_wall = []
        self.dora_indicators = []
        self.dealer = None
        self.clients = clients
        self.agari = Agari()

    def init_round(self):
        self.tiles = [i for i in range(0, 136)]

        # need to change random function in future
        shuffle(self.tiles, shuffle_seed)

        self.dead_wall = self._cut_tiles_from_array(14)
        self.dora_indicators.append(self.dead_wall[8])
        self.dealer = randint(0, 3)
        self.current_client = self.dealer

        for client in self.clients:
            client.player.scores = 250
        player_scores = [i.player.scores for i in self.clients]

        for client in self.clients:
            client.table.init_round(
                self.round_number,
                self.honba_sticks,
                self.riichi_sticks,
                self.dora_indicators[0],
                self.dealer,
                player_scores
            )
            client.init_hand(self._cut_tiles_from_array(13))

    def play_round(self):
        continue_to_play = True

        while continue_to_play:
            client = self.get_current_client()

            tile, in_tempai, is_win = self.draw_tile(client)

            if is_win:
                tiles = self.get_current_client().player.tiles
                tiles.remove(tile)
                logger.info('Tsumo: {0} + {1}'.format(
                    TilesConverter.to_one_line_string(tiles),
                    TilesConverter.to_one_line_string([tile])
                ))
                continue_to_play = False

            if continue_to_play:
                tile = self.discard_tile(client)

                for client in self.clients:
                    if self.can_call_ron(client, tile):
                        logger.info('Ron: {0} + {1}'.format(
                            TilesConverter.to_one_line_string(client.player.tiles),
                            TilesConverter.to_one_line_string([tile])
                        ))
                        continue_to_play = False

                if in_tempai and client.player.can_call_riichi():
                    self.call_riichi(client)

            if continue_to_play:
                self.current_client += 1
                if self.current_client > 3:
                    self.current_client = 0

            if not len(self.tiles):
                continue_to_play = False

        self.round_number += 1

    def draw_tile(self, client):
        tile = self._cut_tiles_from_array(1)[0]
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

    def get_current_client(self) -> Client:
        return self.clients[self.current_client]

    def _cut_tiles_from_array(self, count_of_tiles):
        result = self.tiles[0:count_of_tiles]
        self.tiles = self.tiles[count_of_tiles:len(self.tiles)]
        return result

