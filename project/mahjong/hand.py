# -*- coding: utf-8 -*-
import math
import itertools

from functools import reduce

from mahjong.ai.agari import Agari
from mahjong import yaku
from mahjong.tile import TilesConverter
from mahjong.constants import EAST, SOUTH, WEST, NORTH, CHUN, HATSU, HAKU, TERMINAL_INDICES, HONOR_INDICES


class FinishedHand(object):

    def estimate_hand_value(self,
                            tiles,
                            win_tile,
                            is_tsumo=False,
                            is_riichi=False,
                            is_dealer=False,
                            is_open_hand=False,
                            is_ippatsu=False,
                            is_rinshan=False,
                            is_chankan=False,
                            is_haitei=False,
                            is_houtei=False,
                            is_daburu_riichi=False,
                            is_nagashi_mangan=False,
                            player_wind=None,
                            round_wind=None):
        """
        :param tiles: array with 13 tiles in 136-tile format
        :param win_tile: tile that caused win (ron or tsumo)
        :param is_tsumo:
        :param is_riichi:
        :param is_dealer:
        :param is_open_hand:
        :param is_ippatsu:
        :param is_rinshan:
        :param is_chankan:
        :param is_haitei:
        :param is_houtei:
        :param is_daburu_riichi:
        :param is_nagashi_mangan:
        :param player_wind: index of player wind
        :param round_wind: index of round wind
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

        # special situation
        if is_nagashi_mangan:
            hand_yaku.append(yaku.nagashi_mangan)
            fu = 30
            han = yaku.nagashi_mangan.han['closed']
            cost = self.calculate_scores(han, fu, is_tsumo, is_dealer)
            return return_response()

        if is_riichi and is_open_hand:
            error = "Riichi can't be declared with open hand"
            return return_response()

        if is_ippatsu and is_open_hand:
            error = "Ippatsu can't be declared with open hand"
            return return_response()

        if is_ippatsu and not is_riichi:
            error = "Ippatsu can't be declared without riichi"
            return return_response()

        total_tiles = list(tiles) + [win_tile]
        tiles_34 = TilesConverter.to_34_array(total_tiles)
        divider = HandDivider()

        if not agari.is_agari(tiles_34):
            error = 'Hand is not winning'
            return return_response()

        hand_options = divider.divide_hand(tiles_34)

        costs = []
        for hand in hand_options:
            cost = None
            error = None
            hand_yaku = []
            han = 0
            fu = 0

            if is_tsumo or is_open_hand:
                fu += 20
            else:
                fu += 30

            is_pinfu = self.is_pinfu(tiles, win_tile, hand, player_wind, round_wind)
            if is_pinfu:
                hand_yaku.append(yaku.pinfu)

            is_chitoitsu = self.is_chitoitsu(tiles_34)
            if is_chitoitsu:
                hand_yaku.append(yaku.chiitoitsu)

            if self.is_tanyao(tiles_34):
                hand_yaku.append(yaku.tanyao)

            if is_riichi and not is_daburu_riichi:
                hand_yaku.append(yaku.riichi)

            if is_daburu_riichi:
                hand_yaku.append(yaku.daburu_riichi)

            if is_ippatsu:
                hand_yaku.append(yaku.ippatsu)

            if is_rinshan:
                hand_yaku.append(yaku.rinshan)

            if is_chankan:
                hand_yaku.append(yaku.chankan)

            if is_haitei:
                hand_yaku.append(yaku.haitei)

            if is_houtei:
                hand_yaku.append(yaku.houtei)

            if is_tsumo:
                if not is_open_hand:
                    hand_yaku.append(yaku.tsumo)

                # pinfu + tsumo always is 20 fu
                if not is_pinfu:
                    fu += 2

            if self.is_iipeiko(hand) and not is_open_hand:
                hand_yaku.append(yaku.iipeiko)

            if self.is_toitoi(hand):
                hand_yaku.append(yaku.toitoi)

            if self.is_haku(tiles_34):
                hand_yaku.append(yaku.haku)

            if self.is_hatsu(tiles_34):
                hand_yaku.append(yaku.hatsu)

            if self.is_chun(tiles_34):
                hand_yaku.append(yaku.hatsu)

            if self.is_east(tiles_34, player_wind, round_wind):
                if player_wind == EAST:
                    hand_yaku.append(yaku.yakuhai_place)

                if round_wind == EAST:
                    hand_yaku.append(yaku.yakuhai_round)

            if self.is_south(tiles_34, player_wind, round_wind):
                if player_wind == SOUTH:
                    hand_yaku.append(yaku.yakuhai_place)

                if round_wind == SOUTH:
                    hand_yaku.append(yaku.yakuhai_round)

            if self.is_west(tiles_34, player_wind, round_wind):
                if player_wind == WEST:
                    hand_yaku.append(yaku.yakuhai_place)

                if round_wind == WEST:
                    hand_yaku.append(yaku.yakuhai_round)

            if self.is_north(tiles_34, player_wind, round_wind):
                if player_wind == NORTH:
                    hand_yaku.append(yaku.yakuhai_place)

                if round_wind == NORTH:
                    hand_yaku.append(yaku.yakuhai_round)

            # chitoitsu is always 25 fu
            if is_chitoitsu:
                fu = 25

            # calculate han
            for item in hand_yaku:
                if is_open_hand and item.han['open']:
                    han += item.han['open']
                else:
                    han += item.han['closed']

            # round up
            # 22 -> 30 and etc.
            if fu != 25:
                fu = int(math.ceil(fu / 10.0)) * 10

            if han == 0 or (han == 1 and fu < 30):
                error = 'Not valid han ({0}) and fu ({1})'.format(han, fu)
                return return_response()

            costs.append(self.calculate_scores(han, fu, is_tsumo, is_dealer))

        # let's use cost for most expensive hand
        costs = sorted(costs, key=lambda x: x['main'], reverse=True)
        cost = costs[0]

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

    def is_chitoitsu(self, tiles_34):
        """
        Hand contains only pairs
        :param tiles_34: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        completed_pairs = len([i for i in tiles_34 if i == 2])
        return completed_pairs == 7

    def is_tanyao(self, tiles_34):
        """
        Hand without 1, 9, dragons and winds
        :param tiles_34: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        count_of_terminals = 0
        indices = TERMINAL_INDICES + HONOR_INDICES
        for i in indices:
            if tiles_34[i] > 0:
                count_of_terminals += 1

        return count_of_terminals == 0

    def is_pinfu(self, tiles_34, win_tile, hand, player_wind, round_wind):
        """
        - A hand without pon and kan sets, so it should contains all sequences and a pair
        - The pair should be not valued
        - The waiting must be an open wait (on 2 different tiles)
        :param tiles_34: "136 format" tiles array with 13 tiles
        :param win_tile: "136 format" tile
        :param hand: list of hand's sets
        :return: true|false
        """

        full_hand_tiles = TilesConverter.to_34_array(tiles_34 + [win_tile])
        tiles_34 = TilesConverter.to_34_array(tiles_34)
        win_tile //= 4

        # Syanpon (双ポン). Waiting in the two pairs 44 and 99
        # or seven pairs (chitoitsu)
        count_of_pairs = len([i for i in tiles_34 if i == 2])
        if (tiles_34[win_tile] == 2 and count_of_pairs >= 2) or count_of_pairs == 6:
            return False

        pair = [x for x in hand if len(x) == 2][0][0]
        valued_indices = [HAKU, HATSU, CHUN, player_wind, round_wind]
        if pair in valued_indices:
            return False

        # hand contains a pon or kan
        count_of_pon_or_kan = len([i for i in full_hand_tiles if (i == 3) or (i == 4)])
        if count_of_pon_or_kan > 0:
            return False

        sets = [x for x in hand if (win_tile in x and len(x) == 3)]
        for set_item in sets:
            # penchan waiting: 1-2-...
            if any(x in set_item for x in TERMINAL_INDICES) and set_item.index(win_tile) == 2:
                return False

            # kanchan waiting 5-...-7
            if set_item.index(win_tile) == 1:
                return False

        return True

    def is_iipeiko(self, hand):
        """
        Hand with two identical chi
        :param hand: list of hand's sets
        :return: true|false
        """
        chi = []
        for item in hand:
            if item[0] == item[1] - 1 == item[2] - 2:
                chi.append(item)

        count_of_identical_chi = 0
        for x in chi:
            count = 0
            for y in chi:
                if x == y:
                    count += 1
            if count > count_of_identical_chi:
                count_of_identical_chi = count

        return count_of_identical_chi >= 2

    def is_toitoi(self, hand):
        """
        Hand with two identical chi
        :param hand: list of hand's sets
        :return: true|false
        """
        count_of_pon = len([i for i in hand if (len(i) == 3 and (i[0] == i[1] == i[2]))])
        return count_of_pon == 4

    def is_haku(self, tiles_34):
        """
        Pon of white dragons
        :param tiles_34: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        return tiles_34[HAKU] >= 3

    def is_hatsu(self, tiles_34):
        """
        Pon of green dragons
        :param tiles_34: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        return tiles_34[HATSU] >= 3

    def is_chun(self, tiles_34):
        """
        Pon of red dragons
        :param tiles_34: "34 format" tiles array with 14 tiles
        :return: true|false
        """
        return tiles_34[CHUN] >= 3

    def is_east(self, tiles_34, player_wind, round_wind):
        """
        Pon of east winds
        :param tiles_34: "34 format" tiles array with 14 tiles
        :param player_wind: index of player wind
        :param round_wind: index of round wind
        :return: true|false
        """

        if player_wind and tiles_34[player_wind] >= 3 and player_wind == EAST:
            return True

        if round_wind and tiles_34[round_wind] >= 3 and round_wind == EAST:
            return True

        return False

    def is_south(self, tiles_34, player_wind, round_wind):
        """
        Pon of south winds
        :param tiles_34: "34 format" tiles array with 14 tiles
        :param player_wind: index of player wind
        :param round_wind: index of round wind
        :return: true|false
        """

        if player_wind and tiles_34[player_wind] >= 3 and player_wind == SOUTH:
            return True

        if round_wind and tiles_34[round_wind] >= 3 and round_wind == SOUTH:
            return True

        return False

    def is_west(self, tiles_34, player_wind, round_wind):
        """
        Pon of west winds
        :param tiles_34: "34 format" tiles array with 14 tiles
        :param player_wind: index of player wind
        :param round_wind: index of round wind
        :return: true|false
        """

        if player_wind and tiles_34[player_wind] >= 3 and player_wind == WEST:
            return True

        if round_wind and tiles_34[round_wind] >= 3 and round_wind == WEST:
            return True

        return False

    def is_north(self, tiles_34, player_wind, round_wind):
        """
        Pon of north winds
        :param tiles_34: "34 format" tiles array with 14 tiles
        :param player_wind: index of player wind
        :param round_wind: index of round wind
        :return: true|false
        """

        if player_wind and tiles_34[player_wind] >= 3 and player_wind == NORTH:
            return True

        if round_wind and tiles_34[round_wind] >= 3 and round_wind == NORTH:
            return True

        return False


class HandDivider(object):

    def divide_hand(self, tiles_34):
        """
        Return a list of possible hands.
        :param tiles_34:
        :return:
        """
        pair_indices = self.find_pairs(tiles_34)

        # let's try to find all possible hand options
        hands = []
        for pair_index in pair_indices:
            local_tiles_34 = tiles_34[:]
            # hand = []
            local_tiles_34[pair_index] -= 2

            # 0 - 8 sou tiles
            sou = self.find_valid_combinations(local_tiles_34, 0, 8)

            # 9 - 17 pin tiles
            pin = self.find_valid_combinations(local_tiles_34, 9, 17)

            # 18 - 26 man tiles
            man = self.find_valid_combinations(local_tiles_34, 18, 26)

            honor = []
            for x in HONOR_INDICES:
                if local_tiles_34[x] == 3:
                    honor.append([x] * 3)

            arrays = [[[pair_index] * 2]]
            if sou:
                arrays.append(sou)
            if man:
                arrays.append(man)
            if pin:
                arrays.append(pin)
            if honor:
                arrays.append(honor)

            # let's find all possible hand from our valid sets
            for s in itertools.product(*arrays):
                hand = []
                for item in list(s):
                    if isinstance(item[0], list):
                        for x in item:
                            hand.append(x)
                    else:
                        hand.append(item)

                hand = sorted(hand, key=lambda x: x[0])
                if len(hand) == 5:
                    hands.append(hand)

        if len(pair_indices) == 7:
            hand = []
            for index in pair_indices:
                hand.append([index] * 2)
            hands.append(hand)

        return hands

    def find_pairs(self, tiles_34):
        """
        Find all possible pairs in the hand and return their indices
        :return: array of pair indices
        """
        pair_indices = []
        for x in range(0, 34):
            # ignore pon of honor tiles, because it can't be a part of pair
            if x in HONOR_INDICES and tiles_34[x] != 2:
                continue

            if tiles_34[x] >= 2:
                pair_indices.append(x)

        return pair_indices

    def find_valid_combinations(self, tiles_34, first_index, second_index):
        """
        Find and return all valid set combinations in given suit
        :param tiles_34:
        :param first_index:
        :param second_index:
        :return: list of valid combinations
        """
        indices = []
        for x in range(first_index, second_index + 1):
            if tiles_34[x] > 0:
                indices.extend([x] * tiles_34[x])

        if not indices:
            return []

        all_possible_combinations = list(itertools.permutations(indices, 3))

        def is_valid_combination(item):
            first = item[0]
            second = item[1]
            third = item[2]

            # chi
            if first == second - 1 and first == third - 2:
                return True

            # pon
            if first == second == third:
                return True

            return False

        valid_combinations = []
        for combination in all_possible_combinations:
            if is_valid_combination(combination):
                valid_combinations.append(list(combination))

        if not valid_combinations:
            return []

        count_of_needed_combinations = int(len(indices) / 3)

        # simple case, we have count of sets == count of tiles
        if count_of_needed_combinations == len(valid_combinations) and \
                reduce(lambda x, y: x + y, valid_combinations) == indices:
            return [valid_combinations]

        # filter and remove not possible pon sets
        for item in valid_combinations:
            if item[0] == item[1] == item[2]:
                count_of_sets = 1
                count_of_tiles = 0
                while count_of_sets > count_of_tiles:
                    count_of_tiles = len([x for x in indices if x == item[0]]) / 3
                    count_of_sets = len([x for x in valid_combinations
                                         if x[0] == item[0] and x[1] == item[1] and x[2] == item[2]])

                    if count_of_sets > count_of_tiles:
                        valid_combinations.remove(item)

        # filter and remove not possible chi sets
        for item in valid_combinations:
            if item[0] == item[1] - 1 == item[2] - 2:
                count_of_sets = 5
                # TODO calculate real count of possible sets
                count_of_possible_sets = 4
                while count_of_sets > count_of_possible_sets:
                    count_of_sets = len([x for x in valid_combinations
                                         if x[0] == item[0] and x[1] == item[1] and x[2] == item[2]])

                    if count_of_sets > count_of_possible_sets:
                        valid_combinations.remove(item)

        # hard case - we can build a lot of sets from our tiles
        # for example we have 123456 tiles and we can build sets:
        # [1, 2, 3] [4, 5, 6] [2, 3, 4] [3, 4, 5]
        # and only two of them valid in the same time [1, 2, 3] [4, 5, 6]

        possible_combinations = set(itertools.permutations(
            range(0, len(valid_combinations)), count_of_needed_combinations
        ))

        combinations_results = []
        for combination in possible_combinations:
            result = []
            for item in combination:
                result += valid_combinations[item]
            result = sorted(result)

            if result == indices:
                results = []
                for item in combination:
                    results.append(valid_combinations[item])
                results = sorted(results, key=lambda x: x[0])
                if results not in combinations_results:
                    combinations_results.append(results)

        return combinations_results
