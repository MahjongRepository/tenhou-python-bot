# -*- coding: utf-8 -*-
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_man, is_pin, is_sou, is_pon, is_chi, plus_dora, is_aka_dora, is_honor, is_terminal


class BaseStrategy(object):
    YAKUHAI = 0
    HONITSU = 1
    TANYAO = 2
    FORMAL_TEMPAI = 3
    CHINITSU = 4
    CHIITOITSU = 5

    TYPES = {
        YAKUHAI: 'Yakuhai',
        HONITSU: 'Honitsu',
        TANYAO: 'Tanyao',
        FORMAL_TEMPAI: 'Formal Tempai',
        CHINITSU: 'Chinitsu',
        CHIITOITSU: 'Chiitoitsu'
    }

    not_suitable_tiles = []
    player = None
    type = None
    # number of shanten where we can start to open hand
    min_shanten = 7
    go_for_atodzuke = False

    dora_count_total = 0
    dora_count_central = 0
    dora_count_not_central = 0
    aka_dora_count = 0
    dora_count_honor = 0

    def __init__(self, strategy_type, player):
        self.type = strategy_type
        self.player = player
        self.go_for_atodzuke = False

    def __str__(self):
        return self.TYPES[self.type]

    def should_activate_strategy(self, tiles_136):
        """
        Based on player hand and table situation
        we can determine should we use this strategy or not.
        :param: tiles_136
        :return: boolean
        """
        self.calculate_dora_count(tiles_136)

        if self.player.is_open_hand:
            return True

        return True

    def can_meld_into_agari(self):
        """
        Is melding into agari allowed with this strategy
        :return: boolean
        """
        # By default, the logic is the following: if we have any
        # non-suitable tiles, we can meld into agari state, because we'll
        # throw them away after meld.
        # Otherwise, there is no point.
        for tile in self.player.tiles:
            if not self.is_tile_suitable(tile):
                return True

        return False

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

    def try_to_call_meld(self, tile, is_kamicha_discard, new_tiles):
        """
        Determine should we call a meld or not.
        If yes, it will return Meld object and tile to discard
        :param tile: 136 format tile
        :param is_kamicha_discard: boolean
        :param new_tiles:
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
            melds = self.player.meld_34_tiles + [best_meld_34]
            outs_results, shanten = self.player.ai.calculate_outs(new_tiles, closed_hand, melds)

            # each strategy can use their own value to min shanten number
            if shanten > self.min_shanten:
                return None, None

            # we can't improve hand, so we don't need to open it
            if not outs_results:
                return None, None

            # sometimes we had to call tile, even if it will not improve our hand
            # otherwise we can call only with improvements of shanten
            if not self.meld_had_to_be_called(tile) and shanten >= self.player.ai.shanten:
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

    def calculate_dora_count(self, tiles_136):
        self.dora_count_central = 0
        self.dora_count_not_central = 0
        self.aka_dora_count = 0

        for tile_136 in tiles_136:
            tile_34 = tile_136 // 4

            dora_count = plus_dora(tile_136, self.player.table.dora_indicators)

            if is_aka_dora(tile_136, self.player.table.has_aka_dora):
                self.aka_dora_count += 1

            if not dora_count:
                continue

            if is_honor(tile_34):
                self.dora_count_not_central += dora_count
                self.dora_count_honor += dora_count
            elif is_terminal(tile_34):
                self.dora_count_not_central += dora_count
            else:
                self.dora_count_central += dora_count

        self.dora_count_central += self.aka_dora_count
        self.dora_count_total = self.dora_count_central + self.dora_count_not_central

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
            melds = self.player.meld_34_tiles + [meld]
            shanten = self.player.ai.shanten_calculator.calculate_shanten(completed_hand_34, melds)
            results.append({'shanten': shanten, 'meld': meld})

        results = sorted(results, key=lambda i: i['shanten'])
        return results[0]['meld']
