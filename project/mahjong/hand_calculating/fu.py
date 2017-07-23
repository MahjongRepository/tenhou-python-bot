# -*- coding: utf-8 -*-
from functools import reduce

from mahjong.constants import TERMINAL_INDICES, HONOR_INDICES, HAKU, HATSU, CHUN
from mahjong.utils import is_pair, is_pon, is_chi, simplify


class HandFuCalculator(object):

    def calculate_additional_fu(self, win_tile, hand, is_tsumo, player_wind, round_wind, open_sets, called_kan_indices):
        """
        :param win_tile: "136 format" tile
        :param hand: list of hand's sets
        :param player_wind:
        :param round_wind:
        :param open_sets: array of array with 34 tiles format
        :param called_kan_indices: array of 34 tiles format
        :return: int
        """

        # TODO Refactor it completely

        win_tile //= 4
        additional_fu = 0

        closed_hand = []
        for set_item in hand:
            if not is_pair(set_item) and set_item not in open_sets:
                closed_hand.append(set_item)

        pon_sets = [x for x in hand if is_pon(x)]
        chi_sets = [x for x in hand if (win_tile in x and is_chi(x))]
        closed_hand_indices = closed_hand and reduce(lambda z, y: z + y, closed_hand) or []

        # there is no sense to check identical sets
        unique_chi_sets = []
        for item in chi_sets:
            if item not in unique_chi_sets:
                unique_chi_sets.append(item)

        chi_fu_sets = []
        for set_item in unique_chi_sets:
            count_of_open_sets = len([x for x in open_sets if x == set_item])
            count_of_sets = len([x for x in chi_sets if x == set_item])
            if count_of_open_sets == count_of_sets:
                continue

            # penchan waiting
            if any(x in set_item for x in TERMINAL_INDICES):
                tile_number = simplify(win_tile)
                # 1-2-...
                if set_item.index(win_tile) == 2 and tile_number == 2:
                    chi_fu_sets.append(set_item)
                # ...-8-9
                elif set_item.index(win_tile) == 0 and tile_number == 6:
                    chi_fu_sets.append(set_item)

            # kanchan waiting 5-...-7
            if set_item.index(win_tile) == 1:
                chi_fu_sets.append(set_item)

        for set_item in pon_sets:
            set_was_open = set_item in open_sets
            is_kan = set_item[0] in called_kan_indices
            is_honor = set_item[0] in TERMINAL_INDICES + HONOR_INDICES

            # we win on the third pon tile, our pon will be count as open
            if not is_tsumo and win_tile in set_item:
                # 111123 form is exception
                if len([x for x in closed_hand_indices if x == win_tile]) != 4:
                    set_was_open = True

            if is_honor:
                if is_kan:
                    additional_fu += set_was_open and 16 or 32
                else:
                    additional_fu += set_was_open and 4 or 8
            else:
                if is_kan:
                    additional_fu += set_was_open and 8 or 16
                else:
                    additional_fu += set_was_open and 2 or 4

        # valued pair
        pair = [x for x in hand if is_pair(x)][0][0]
        valued_indices = [HAKU, HATSU, CHUN, player_wind, round_wind]
        count_of_valued_pairs = [x for x in valued_indices if x == pair]
        if len(count_of_valued_pairs):
            # we can have 4 fu for east-east pair
            additional_fu += 2 * len(count_of_valued_pairs)

        pair_was_counted = False
        if len(chi_fu_sets) and len(unique_chi_sets) == len(chi_fu_sets):
            if len(chi_fu_sets) == 1 and pair in chi_fu_sets[0] and win_tile == pair:
                additional_fu += 2
                pair_was_counted = True
            else:
                additional_fu += 2
                pair_was_counted = True
        elif additional_fu != 0 and len(chi_fu_sets):
            # Hand like 123345
            # we can't count pinfu yaku here, so let's add additional fu for 123 waiting
            pair_was_counted = True
            additional_fu += 2

        # separate pair waiting
        if pair == win_tile:
            if not len(chi_sets):
                additional_fu += 2
            elif additional_fu != 0 and not pair_was_counted:
                # we can't count pinfu yaku here, so let's add additional fu
                additional_fu += 2

        return additional_fu
