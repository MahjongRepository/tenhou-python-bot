# -*- coding: utf-8 -*-
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_man, is_pin, is_sou, is_chi, is_pon


class BaseStrategy(object):
    YAKUHAI = 0
    HONITSU = 1
    TANYAO = 2

    TYPES = {
        YAKUHAI: 'Yakuhai',
        HONITSU: 'Honitsu',
        TANYAO: 'Tanyao',
    }

    player = None
    type = None
    # number of shanten where we can start to open hand
    min_shanten = 7

    def __init__(self, strategy_type, player):
        self.type = strategy_type
        self.player = player

    def __str__(self):
        return self.TYPES[self.type]

    def should_activate_strategy(self):
        """
        Based on player hand and table situation
        we can determine should we use this strategy or not
        :return: boolean
        """
        raise NotImplemented()

    def is_tile_suitable(self, tile):
        """
        Can tile be used for open hand strategy or not
        :param tile: in 136 tiles format
        :return: boolean
        """
        raise NotImplemented()

    def try_to_call_meld(self, tile, enemy_seat):
        """
        Determine should we call a meld or not.
        If yes, it will return Meld object and tile to discard
        :param tile: 136 format tile
        :param enemy_seat: 1, 2, 3
        :return: meld and tile to discard after called open set
        """
        if self.player.in_riichi:
            return None, None

        closed_hand = self.player.closed_hand[:]

        # we opened all our hand
        if len(closed_hand) == 1:
            return None, None

        # we can't use this tile for our chosen strategy
        if not self.is_tile_suitable(tile):
            return None, None

        discarded_tile = tile // 4
        # previous player
        is_kamicha_discard = self.player.seat - 1 == enemy_seat or self.player.seat == 0 and enemy_seat == 3

        new_tiles = self.player.tiles[:] + [tile]
        outs_results, shanten = self.player.ai.calculate_outs(new_tiles, closed_hand)

        # each strategy can use their own value to min shanten number
        if shanten > self.min_shanten:
            return None, None

        # we can't improve hand, so we don't need to open it
        if not outs_results:
            return None, None

        # tile will decrease the count of shanten in hand
        # so let's call opened set with it
        if shanten < self.player.ai.previous_shanten:
            closed_hand_34 = TilesConverter.to_34_array(closed_hand + [tile])

            combinations = []
            first_index = 0
            second_index = 0
            first_limit = 0
            second_limit = 0
            if is_man(discarded_tile):
                first_index = 0
                second_index = 8
            elif is_pin(discarded_tile):
                first_index = 9
                second_index = 17
            elif is_sou(discarded_tile):
                first_index = 18
                second_index = 26

            if second_index == 0:
                # honor tiles
                if closed_hand_34[discarded_tile] == 3:
                    combinations = [[[discarded_tile] * 3]]
            else:
                # to avoid not necessary calculations
                # we can check only tiles around +-2 discarded tile
                first_limit = discarded_tile - 2
                if first_limit < first_index:
                    first_limit = 0
                second_limit = discarded_tile + 2
                if second_limit > second_index:
                    second_limit = second_index

                combinations = self.player.ai.hand_divider.find_valid_combinations(closed_hand_34,
                                                                                   first_limit,
                                                                                   second_limit, True)

            if combinations:
                combinations = combinations[0]

            possible_melds = []
            for combination in combinations:
                # we can call pon from everyone
                if is_pon(combination) and discarded_tile in combination:
                    if combination not in possible_melds:
                        possible_melds.append(combination)

                # we can call chi only from left player
                if is_chi(combination) and is_kamicha_discard and discarded_tile in combination:
                    if combination not in possible_melds:
                        possible_melds.append(combination)

            # we can call melds only with allowed tiles
            validated_melds = []
            for meld in possible_melds:
                if (self.is_tile_suitable(meld[0] * 4) and
                        self.is_tile_suitable(meld[1] * 4) and
                        self.is_tile_suitable(meld[2] * 4)):
                    validated_melds.append(meld)
            possible_melds = validated_melds

            if len(possible_melds):
                combination = self._find_best_meld_to_open(possible_melds, closed_hand_34, first_limit, second_limit)
                meld_type = is_chi(combination) and Meld.CHI or Meld.PON
                combination.remove(discarded_tile)

                first_tile = TilesConverter.find_34_tile_in_136_array(combination[0], closed_hand)
                closed_hand.remove(first_tile)

                second_tile = TilesConverter.find_34_tile_in_136_array(combination[1], closed_hand)
                closed_hand.remove(second_tile)

                tiles = [
                    first_tile,
                    second_tile,
                    tile
                ]

                meld = Meld()
                meld.who = self.player.seat
                meld.from_who = enemy_seat
                meld.type = meld_type
                meld.tiles = sorted(tiles)

                tile_to_discard = None
                # we need to find possible tile to discard
                # it can be that first result already on our set
                for out_result in outs_results:
                    tile_34 = out_result['discard']
                    tile_to_discard = TilesConverter.find_34_tile_in_136_array(tile_34, closed_hand)
                    if tile_to_discard:
                        break

                return meld, tile_to_discard

        return None, None

    def _find_best_meld_to_open(self, possible_melds, closed_hand_34, first_limit, second_limit):
        """
        For now best meld will be the meld with higher count of remaining sets in the hand
        :param possible_melds:
        :param closed_hand_34:
        :param first_limit:
        :param second_limit:
        :return:
        """

        if len(possible_melds) == 1:
            return possible_melds[0]

        best_meld = None
        best_option = -2

        for combination in possible_melds:
            remaining_hand = []
            local_closed_hand_34 = closed_hand_34[:]

            # remove combination from hand and let's see what we will hand in the end
            local_closed_hand_34[combination[0]] -= 1
            local_closed_hand_34[combination[1]] -= 1
            local_closed_hand_34[combination[2]] -= 1

            pair_indices = self.player.ai.hand_divider.find_pairs(local_closed_hand_34,
                                                                  first_limit,
                                                                  second_limit)

            if pair_indices:
                for pair_index in pair_indices:
                    pair_34 = local_closed_hand_34[:]
                    pair_34[pair_index] -= 2

                    hand = [[[pair_index] * 2]]

                    pair_combinations = self.player.ai.hand_divider.find_valid_combinations(pair_34,
                                                                                            first_limit,
                                                                                            second_limit, True)
                    if pair_combinations:
                        hand.append(pair_combinations)

                    remaining_hand.append(hand)

            local_combinations = self.player.ai.hand_divider.find_valid_combinations(local_closed_hand_34,
                                                                                     first_limit,
                                                                                     second_limit, True)

            if local_combinations:
                for pair_index in pair_indices:
                    local_combinations.append([[pair_index] * 2])
                remaining_hand.append(local_combinations)

            most_long_hand = -1
            for item in remaining_hand:
                if len(item) > most_long_hand:
                    most_long_hand = len(item)

            if most_long_hand > best_option:
                best_option = most_long_hand
                best_meld = combination

        return best_meld
