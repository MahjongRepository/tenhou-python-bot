# -*- coding: utf-8 -*-
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_man, is_pin, is_sou, is_chi, is_pon


class BaseStrategy(object):
    YAKUHAI = 0

    player = None
    type = None

    def __init__(self, type, player):
        self.type = type
        self.player = player

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

        # we can't improve hand, so we don't need to open it
        if not outs_results:
            return None, None

        # tile will decrease the count of shanten in hand
        # so let's call opened set with it
        if shanten < self.player.ai.previous_shanten:
            closed_hand_34 = TilesConverter.to_34_array(closed_hand + [tile])

            combinations = []
            if is_man(discarded_tile):
                combinations = self.player.ai.hand_divider.find_valid_combinations(closed_hand_34, 0, 8, True)
            elif is_pin(discarded_tile):
                combinations = self.player.ai.hand_divider.find_valid_combinations(closed_hand_34, 9, 17, True)
            elif is_sou(discarded_tile):
                combinations = self.player.ai.hand_divider.find_valid_combinations(closed_hand_34, 18, 26, True)
            else:
                # honor tiles
                if closed_hand_34[discarded_tile] == 3:
                    combinations = [[[discarded_tile] * 3]]

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

            if len(possible_melds):
                # TODO add logic to find best meld
                combination = possible_melds[0]
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
