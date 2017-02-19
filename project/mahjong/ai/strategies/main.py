# -*- coding: utf-8 -*-
from mahjong.ai.discard import DiscardOption
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
        we can determine should we use this strategy or not.
        For now default rule for all strategies: don't open hand with 5+ pairs
        :return: boolean
        """
        if self.player.is_open_hand:
            return True

        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        count_of_pairs = len([x for x in range(0, 34) if tiles_34[x] >= 2])

        return count_of_pairs < 5

    def is_tile_suitable(self, tile):
        """
        Can tile be used for open hand strategy or not
        :param tile: in 136 tiles format
        :return: boolean
        """
        raise NotImplemented()

    def determine_what_to_discard(self, closed_hand, outs_results, shanten, for_open_hand, tile_for_open_hand):
        """
        :param closed_hand: array of 136 tiles format
        :param outs_results: dict
        :param shanten: number of shanten
        :param for_open_hand: boolean
        :param tile_for_open_hand: 136 tile format
        :return: array of DiscardOption
        """

        # mark all not suitable tiles as ready to discard
        # even if they not should be discarded by uke-ire
        for i in closed_hand:
            i //= 4

            if not self.is_tile_suitable(i * 4):
                item_was_found = False
                for j in outs_results:
                    if j.tile_to_discard == i:
                        item_was_found = True
                        j.tiles_count = 1000
                        j.waiting = []

                if not item_was_found:
                    outs_results.append(DiscardOption(player=self.player,
                                                      tile_to_discard=i,
                                                      waiting=[],
                                                      tiles_count=1000))

        return outs_results

    def try_to_call_meld(self, tile, is_kamicha_discard):
        """
        Determine should we call a meld or not.
        If yes, it will return Meld object and tile to discard
        :param tile: 136 format tile
        :param is_kamicha_discard: boolean
        :return: meld and tile to discard after called open set, and new shanten count
        """
        if self.player.in_riichi:
            return None, None, None

        closed_hand = self.player.closed_hand[:]

        # we opened all our hand
        if len(closed_hand) == 1:
            return None, None, None

        # we can't use this tile for our chosen strategy
        if not self.is_tile_suitable(tile):
            return None, None, None

        discarded_tile = tile // 4

        new_tiles = self.player.tiles[:] + [tile]
        # we need to calculate count of shanten with open hand condition
        # to exclude chitoitsu from the calculation
        outs_results, shanten = self.player.ai.calculate_outs(new_tiles, closed_hand, is_open_hand=True)

        # each strategy can use their own value to min shanten number
        if shanten > self.min_shanten:
            return None, None, None

        # we can't improve hand, so we don't need to open it
        if not outs_results:
            return None, None, None

        # tile will decrease the count of shanten in hand
        # so let's call opened set with it
        if shanten < self.player.ai.previous_shanten or self.meld_had_to_be_called(tile):
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
                meld.type = meld_type
                meld.tiles = sorted(tiles)

                results = self.determine_what_to_discard(closed_hand, outs_results, shanten, True, tile)
                # we don't have tiles to discard after hand opening
                # so, we don't need to open hand
                if not results:
                    return None, None, None

                tile_to_discard = self.player.ai.chose_tile_to_discard(results, closed_hand)
                # 0 tile is possible, so we can't just use "if tile_to_discard"
                if tile_to_discard is not None:
                    return meld, tile_to_discard, shanten

        return None, None, None

    def meld_had_to_be_called(self, tile):
        """
        For special cases meld had to be called even if shanten number will not be increased
        :param tile: in 136 tiles format
        :return: boolean
        """
        return False

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
