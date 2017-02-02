# -*- coding: utf-8 -*-
from mahjong.constants import HONOR_INDICES
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_man, is_pin, is_sou, is_chi, is_pon, find_isolated_tile_indices


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

    def determine_what_to_discard(self, closed_hand, outs_results, shanten):
        """
        :param closed_hand: array of 136 tiles format
        :param outs_results: dict
        :param shanten: number of shanten
        :return: tile in 136 format or none
        """
        tile_to_discard = None
        for out_result in outs_results:
            tile_34 = out_result['discard']
            tile_to_discard = TilesConverter.find_34_tile_in_136_array(tile_34, closed_hand)
            if tile_to_discard:
                break
        return tile_to_discard

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
        # we need to calculate count of shanten with open hand condition
        # to exclude chitoitsu from the calculation
        outs_results, shanten = self.player.ai.calculate_outs(new_tiles, closed_hand, is_open_hand=True)

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
                combination = self._find_best_meld_to_open(possible_melds, closed_hand_34, first_limit, second_limit,
                                                           new_tiles)
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

                tile_to_discard = self.determine_what_to_discard(closed_hand, outs_results, shanten)
                if tile_to_discard:
                    return meld, tile_to_discard

        return None, None

    def _find_best_meld_to_open(self, possible_melds, closed_hand_34, first_limit, second_limit, completed_hand):
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

        # For now we will replace possible set with one completed pon set
        # and we will calculate remaining shanten in the hand
        # and chose the hand with min shanten count
        completed_hand_34 = TilesConverter.to_34_array(completed_hand)
        tile_to_replace = None
        isolated_tiles = find_isolated_tile_indices(completed_hand_34)
        if isolated_tiles:
            tile_to_replace = isolated_tiles[0]

        if not tile_to_replace:
            return possible_melds[0]

        results = []
        for meld in possible_melds:
            temp_hand_34 = completed_hand_34[:]
            temp_hand_34[meld[0]] -= 1
            temp_hand_34[meld[1]] -= 1
            temp_hand_34[meld[2]] -= 1
            temp_hand_34[tile_to_replace] = 3
            # open hand always should be true to exclude chitoitsu hands from calculations
            shanten = self.player.ai.shanten.calculate_shanten(temp_hand_34, True, self.player.meld_tiles)
            results.append({'shanten': shanten, 'meld': meld})

        results = sorted(results, key=lambda i: i['shanten'])
        return results[0]['meld']
