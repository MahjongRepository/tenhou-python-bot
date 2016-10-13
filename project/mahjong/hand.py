# -*- coding: utf-8 -*-
import math

from mahjong.ai.agari import Agari
from mahjong import yaku
from mahjong.tile import TilesConverter


class FinishedHand(object):
    # 1 and 9
    terminal_indices = [0, 8, 9, 17, 18, 26]
    # dragons and winds
    honor_indices = [27, 28, 29, 30, 31, 32, 33]

    def estimate_hand_value(self, tiles, win_tile, is_tsumo=False, is_riichi=False, is_dealer=False,
                            is_open_hand=False):
        """
        :param tiles: array with 13 tiles in 136-tile format
        :param win_tile: tile that caused win (ron or tsumo)
        :param is_tsumo:
        :param is_riichi:
        :param is_dealer:
        :param is_open_hand:
        :return: The dictionary with hand cost or error response

        {"cost": {'main': 1000, 'additional': 0}, "han": 1, "fu": 30, "error": None, "hand_yaku": []}
        {"cost": None, "han": 0, "fu": 0, "error": "Hand is not valid", "hand_yaku": []}
        """
        agari = Agari()
        cost = None
        error = None

        hand_yaku = []
        han = 0
        fu = 0

        def return_response():
            return {'cost': cost, 'error': error, 'han': han, 'fu': fu, 'hand_yaku': hand_yaku}

        if is_riichi and is_open_hand:
            error = 'Hand can\'t be open with riichi'
            return return_response()

        total_tiles = list(tiles) + [win_tile]
        tiles_34 = TilesConverter.to_34_array(total_tiles)
        if not agari.is_agari(tiles_34):
            error = 'Hand is not winning'
            return return_response()

        if is_tsumo or is_open_hand:
            fu += 20
        else:
            fu += 30

        is_pinfu = self.is_pinfu(tiles, win_tile)
        if is_pinfu:
            hand_yaku.append(yaku.pinfu)

        is_chitoitsu = self.is_chitoitsu(tiles_34)
        if is_chitoitsu:
            hand_yaku.append(yaku.chiitoitsu)

        if self.is_tanyao(tiles_34):
            hand_yaku.append(yaku.tanyao)

        if is_riichi:
            hand_yaku.append(yaku.riichi)

        if is_tsumo:
            hand_yaku.append(yaku.tsumo)
            # pinfu + tsumo always is 20 fu
            if not is_pinfu:
                fu += 2

        if self.is_haku(tiles_34):
            hand_yaku.append(yaku.haku)

        if self.is_hatsu(tiles_34):
            hand_yaku.append(yaku.hatsu)

        if self.is_chun(tiles_34):
            hand_yaku.append(yaku.hatsu)

        # chitoitsu is always 25 fu
        if is_chitoitsu:
            fu = 25

        # calculate han
        for item in hand_yaku:
            if is_open_hand and item.han['open']:
                han += item.han['open']
            else:
                han += item.han['closed']

        if han == 0 or (han == 1 and fu < 30):
            error = 'Not valid han ({0}) and fu ({1})'.format(han, fu)
            return return_response()

        cost = self.calculate_scores(han, fu, is_tsumo, is_dealer)

        return return_response()

    def calculate_scores(self, han, fu, is_tsumo, is_dealer):
        """
        Calculate how much scores cost a hand with given han and fu
        :param han:
        :param fu:
        :param is_tsumo:
        :param is_dealer:
        :return: a dictionary with main and additional cost
        for ron additional cost is always = 0
        for tsumo main cost is cost for dealer and additional is cost for player
        {'main': 1000, 'additional': 0}
        """
        if han >= 5:
            # yakuman
            if han >= 13:
                rounded = 8000
            # sanbaiman
            elif han >= 11:
                rounded = 6000
            # baiman
            elif han >= 8:
                rounded = 4000
            # haneman
            elif han >= 6:
                rounded = 3000
            else:
                rounded = 2000

            double_rounded = rounded * 2
            four_rounded = double_rounded * 2
            six_rounded = double_rounded * 3
        else:
            base_points = fu * pow(2, 2 + han)
            rounded = math.ceil(base_points / 100.) * 100
            double_rounded = math.ceil(2 * base_points / 100.) * 100
            four_rounded = math.ceil(4 * base_points / 100.) * 100
            six_rounded = math.ceil(6 * base_points / 100.) * 100

            # mangan
            if rounded >= 2000:
                rounded = 2000
                double_rounded = rounded * 2
                four_rounded = double_rounded * 2
                six_rounded = double_rounded * 3

            # kiriage mangan
            if han == 4 and fu == 30:
                rounded = 2000
                double_rounded = 3900
                four_rounded = 7700
                six_rounded = 11600

        if is_tsumo:
            return {'main': double_rounded, 'additional': rounded}
        else:
            return {'main': is_dealer and six_rounded or four_rounded, 'additional': 0}

    def is_chitoitsu(self, tiles):
        """
        Hand contains only pairs
        :param tiles: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        completed_pairs = len([i for i in tiles if i == 2])
        return completed_pairs == 7

    def is_tanyao(self, tiles):
        """
        Hand without 1, 9, dragons and winds
        :param tiles: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        count_of_terminals = 0
        indices = self.terminal_indices + self.honor_indices
        for i in indices:
            if tiles[i] > 0:
                count_of_terminals += 1

        return count_of_terminals == 0

    def is_pinfu(self, tiles, win_tile):
        """
        This is a draft. Should be improved to process crossed cases

        - A hand without pon and kan, so it should contains all sequences and a pair
        - The pair must value be 0 fu
        - The waiting must be an open wait (on 2 different tiles)
        :param tiles: "136 format" tiles array with 13 tiles
        :param win_tile: "136 format" tile
        :return: true|false
        """

        is_pinfu = True

        full_hand_tiles = TilesConverter.to_34_array(tiles + [win_tile])
        tiles = TilesConverter.to_34_array(tiles)
        win_tile //= 4

        # Syanpon (双ポン). Waiting in the two pairs 44 and 99
        # or seven pairs (chitoitsu)
        count_of_pairs = len([i for i in tiles if i == 2])
        if (tiles[win_tile] == 2 and count_of_pairs >= 2) or count_of_pairs == 6:
            is_pinfu = False

        # hand contains a pon or kan
        count_of_pon_or_kan = len([i for i in full_hand_tiles if (i == 3) or (i == 4)])
        if count_of_pon_or_kan > 0:
            is_pinfu = False

        return is_pinfu

    def is_haku(self, tiles):
        """
        Pon of white dragons
        :param tiles: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        return tiles[31] >= 3

    def is_hatsu(self, tiles):
        """
        Pon of green dragons
        :param tiles: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        return tiles[32] >= 3

    def is_chun(self, tiles):
        """
        Pon of red dragons
        :param tiles: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        return tiles[33] >= 3
