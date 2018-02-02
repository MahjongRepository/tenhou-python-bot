# -*- coding: utf-8 -*-
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_man, is_pin, is_sou, is_pon, is_chi


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

    def determine_what_to_discard(self, closed_hand, outs_results, shanten, for_open_hand, tile_for_open_hand,
                                  hand_was_open=False):
        """

        "for_open_hand" and "tile_for_open_hand" we had to use when we want to
        determine what melds will be open

        "hand_was_open" we will use in rare cases
        when we open hand and before meld was added to the player
        it happens between we send a message to tenhou and tenhou send confirmation message to us
        sometimes we failed to call a meld because of other player

        :param closed_hand: array of 136 tiles format
        :param outs_results: dict
        :param shanten: number of shanten
        :param for_open_hand: boolean
        :param tile_for_open_hand: 136 tile format
        :param hand_was_open: boolean
        :return: array of DiscardOption
        """

        # for riichi we don't need to discard useful tiles
        if shanten == 0 and not self.player.is_open_hand:
            return outs_results

        # mark all not suitable tiles as ready to discard
        # even if they not should be discarded by uke-ire
        for j in outs_results:
            if not self.is_tile_suitable(j.tile_to_discard * 4):
                j.had_to_be_discarded = True

        return outs_results

    def try_to_call_meld(self, tile, is_kamicha_discard):
        """
        Determine should we call a meld or not.
        If yes, it will return Meld object and tile to discard
        :param tile: 136 format tile
        :param is_kamicha_discard: boolean
        :return: Meld and DiscardOption objects
        """
        if self.player.in_riichi:
            return None, None

        if self.player.ai.in_defence:
            return None, None

        closed_hand = self.player.closed_hand[:]

        # we can't open hand anymore
        if len(closed_hand) == 1:
            return None, None

        # we can't use this tile for our chosen strategy
        if not self.is_tile_suitable(tile):
            return None, None

        discarded_tile = tile // 4
        new_tiles = self.player.tiles[:] + [tile]
        closed_hand_34 = TilesConverter.to_34_array(closed_hand + [tile])

        combinations = []
        first_index = 0
        second_index = 0
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
                first_limit = first_index

            second_limit = discarded_tile + 2
            if second_limit > second_index:
                second_limit = second_index

            combinations = self.player.ai.hand_divider.find_valid_combinations(closed_hand_34,
                                                                               first_limit,
                                                                               second_limit, True)

        if combinations:
            combinations = combinations[0]

        possible_melds = []
        for best_meld_34 in combinations:
            # we can call pon from everyone
            if is_pon(best_meld_34) and discarded_tile in best_meld_34:
                if best_meld_34 not in possible_melds:
                    possible_melds.append(best_meld_34)

            # we can call chi only from left player
            if is_chi(best_meld_34) and is_kamicha_discard and discarded_tile in best_meld_34:
                if best_meld_34 not in possible_melds:
                    possible_melds.append(best_meld_34)

        # we can call melds only with allowed tiles
        validated_melds = []
        for meld in possible_melds:
            if (self.is_tile_suitable(meld[0] * 4) and
                    self.is_tile_suitable(meld[1] * 4) and
                    self.is_tile_suitable(meld[2] * 4)):
                validated_melds.append(meld)
        possible_melds = validated_melds

        if not possible_melds:
            return None, None

        best_meld_34 = self._find_best_meld_to_open(possible_melds, new_tiles)
        if best_meld_34:
            # we need to calculate count of shanten with supposed meld
            # to prevent bad hand openings
            melds = self.player.open_hand_34_tiles + [best_meld_34]
            outs_results, shanten = self.player.ai.calculate_outs(new_tiles, closed_hand, melds)

            # each strategy can use their own value to min shanten number
            if shanten > self.min_shanten:
                return None, None

            # we can't improve hand, so we don't need to open it
            if not outs_results:
                return None, None

            # sometimes we had to call tile, even if it will not improve our hand
            # otherwise we can call only with improvements of shanten
            if not self.meld_had_to_be_called(tile) and shanten >= self.player.ai.previous_shanten:
                return None, None

            meld_type = is_chi(best_meld_34) and Meld.CHI or Meld.PON
            best_meld_34.remove(discarded_tile)

            first_tile = TilesConverter.find_34_tile_in_136_array(best_meld_34[0], closed_hand)
            closed_hand.remove(first_tile)

            second_tile = TilesConverter.find_34_tile_in_136_array(best_meld_34[1], closed_hand)
            closed_hand.remove(second_tile)

            tiles = [
                first_tile,
                second_tile,
                tile
            ]

            meld = Meld()
            meld.type = meld_type
            meld.tiles = sorted(tiles)

            # we had to be sure that all our discard results exists in the closed hand
            filtered_results = []
            for result in outs_results:
                if result.find_tile_in_hand(closed_hand):
                    filtered_results.append(result)

            # we can't discard anything, so let's not open our hand
            if not filtered_results:
                return None, None

            selected_tile = self.player.ai.process_discard_options_and_select_tile_to_discard(
                filtered_results,
                shanten,
                had_was_open=True
            )

            return meld, selected_tile

        return None, None

    def meld_had_to_be_called(self, tile):
        """
        For special cases meld had to be called even if shanten number will not be increased
        :param tile: in 136 tiles format
        :return: boolean
        """
        return False

    def _find_best_meld_to_open(self, possible_melds, completed_hand):
        """
        :param possible_melds:
        :param completed_hand:
        :return:
        """

        if len(possible_melds) == 1:
            return possible_melds[0]

        # We will replace possible set with one completed pon set
        # and we will calculate remaining shanten in the hand
        # and chose the hand with min shanten count
        completed_hand_34 = TilesConverter.to_34_array(completed_hand)

        results = []
        for meld in possible_melds:
            melds = self.player.open_hand_34_tiles + [meld]
            shanten = self.player.ai.shanten.calculate_shanten(completed_hand_34, melds)
            results.append({'shanten': shanten, 'meld': meld})

        results = sorted(results, key=lambda i: i['shanten'])
        return results[0]['meld']
