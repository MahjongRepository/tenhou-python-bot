# -*- coding: utf-8 -*-
from mahjong.ai.agari import Agari


class FinishedHand(object):

    @classmethod
    def estimate_hand_value(cls, tiles, win_tile, is_tsumo, is_riichi, is_dealer, is_open_hand):
        """
        :param tiles: array with 13 tiles in 136-tile format
        :param win_tile: tile that caused win (ron or tsumo)
        :return: The dictionary with hand cost or error response
        {"cost": 1000, "han": 1, "fu": 30, "error": None}
        {"cost": None, "han": 0, "fu": 0, "error": "Hand is not valid"}
        """
        agari = Agari()
        cost = None
        error = None

        hand_yaku = []
        han = 0
        fu = 0

        def return_response():
            return {'cost': cost, 'error': error, 'han': han, 'fu': fu}

        # total_tiles = list(tiles) + [win_tile]
        # if not agari.is_agari(total_tiles):
        #     error = 'Hand is not winning'
        #     return return_response()

        if han == 1 and fu < 30:
            error = 'Not valid han and fu'
            return return_response()

        return 1000
