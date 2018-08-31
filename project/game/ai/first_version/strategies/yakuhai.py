# -*- coding: utf-8 -*-
from mahjong.constants import EAST, SOUTH
from mahjong.meld import Meld
from mahjong.tile import TilesConverter

from game.ai.first_version.strategies.main import BaseStrategy


class YakuhaiStrategy(BaseStrategy):
    valued_pairs = None
    has_valued_pon = None

    def __init__(self, strategy_type, player):
        super().__init__(strategy_type, player)

        self.valued_pairs = []
        self.has_valued_pon = False

    def should_activate_strategy(self, tiles_136):
        """
        We can go for yakuhai strategy if we have at least one yakuhai pair in the hand
        :return: boolean
        """
        result = super(YakuhaiStrategy, self).should_activate_strategy(tiles_136)
        if not result:
            return False

        tiles_34 = TilesConverter.to_34_array(tiles_136)
        player_hand_tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        self.valued_pairs = [x for x in self.player.valued_honors if tiles_34[x] >= 2]

        is_double_east_wind = len([x for x in self.valued_pairs if x == EAST]) == 2
        is_double_south_wind = len([x for x in self.valued_pairs if x == SOUTH]) == 2

        self.valued_pairs = list(set(self.valued_pairs))
        self.has_valued_pon = len([x for x in self.player.valued_honors if tiles_34[x] == 3]) >= 1

        has_valued_pair = False

        for pair in self.valued_pairs:
            # we have valued pair in the hand and there are enough tiles
            # in the wall
            if self.player.total_tiles(pair, player_hand_tiles_34) < 4:
                has_valued_pair = True
                break

        # we don't have valuable pair to open our hand
        if not has_valued_pair:
            return False

        # let's always open double east
        if is_double_east_wind:
            return True

        # let's open double south if we have a dora in the hand
        # or we have other valuable pairs
        if is_double_south_wind and (self.dora_count_total >= 1 or len(self.valued_pairs) >= 2):
            return True

        # If we have 1+ dora in the hand and there are 2+ valuable pairs let's open hand
        if len(self.valued_pairs) >= 2 and self.dora_count_total >= 1:
            return True

        # If we have 2+ dora in the hand let's open hand
        if self.dora_count_total >= 2:
            for x in range(0, 34):
                # we have other pair in the hand
                # so we can open hand for atodzuke
                if tiles_34[x] >= 2 and x not in self.valued_pairs:
                    self.go_for_atodzuke = True
            return True

        # If we have 1+ dora in the hand and there is 5+ round step let's open hand
        if self.dora_count_total >= 1 and self.player.round_step > 5:
            return True

        for pair in self.valued_pairs:
            # this valuable tile was discarded once
            # let's open on it in that case
            if self.player.total_tiles(pair, player_hand_tiles_34) == 3 and self.player.ai.shanten > 1:
                return True

        return False

    def is_tile_suitable(self, tile):
        """
        For yakuhai we don't have any limits
        :param tile: 136 tiles format
        :return: True
        """
        return True

    def determine_what_to_discard(self, closed_hand, outs_results, shanten, for_open_hand, tile_for_open_hand,
                                  hand_was_open=False):
        if tile_for_open_hand:
            tile_for_open_hand //= 4

        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        valued_pairs = [x for x in self.player.valued_honors if tiles_34[x] == 2]

        # when we trying to open hand with tempai state, we need to chose a valued pair waiting
        if shanten == 0 and valued_pairs and for_open_hand and tile_for_open_hand not in valued_pairs:
            valued_pair = valued_pairs[0]

            results = []
            for item in outs_results:
                if valued_pair in item.waiting:
                    results.append(item)
            return results

        if self.player.is_open_hand:
            has_yakuhai_pon = any([self._is_yakuhai_pon(meld) for meld in self.player.melds])
            # we opened our hand for atodzuke
            if not has_yakuhai_pon:
                for item in outs_results:
                    for valued_pair in valued_pairs:
                        if valued_pair == item.tile_to_discard:
                            item.had_to_be_saved = True

        return super(YakuhaiStrategy, self).determine_what_to_discard(closed_hand,
                                                                      outs_results,
                                                                      shanten,
                                                                      for_open_hand,
                                                                      tile_for_open_hand,
                                                                      hand_was_open)

    def meld_had_to_be_called(self, tile):
        # for closed hand we don't need to open hand with special conditions
        if not self.player.is_open_hand:
            return False

        tile //= 4
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        valued_pairs = [x for x in self.player.valued_honors if tiles_34[x] == 2]

        for meld in self.player.melds:
            # for big shanten number we don't need to check already opened pon set,
            # because it will improve pur hand anyway
            if self.player.ai.shanten >= 1:
                break

            # we have already opened yakuhai pon
            # so we don't need to open hand without shanten improvement
            if self._is_yakuhai_pon(meld):
                return False

        # open hand for valued pon
        for valued_pair in valued_pairs:
            if valued_pair == tile:
                return True

        return False

    def try_to_call_meld(self, tile, is_kamicha_discard, tiles_136):
        if self.has_valued_pon:
            return super(YakuhaiStrategy, self).try_to_call_meld(tile, is_kamicha_discard, tiles_136)

        tile_34 = tile // 4
        # we will open hand for atodzuke only in the special cases
        if not self.player.is_open_hand and tile_34 not in self.valued_pairs:
            if self.go_for_atodzuke:
                return super(YakuhaiStrategy, self).try_to_call_meld(tile, is_kamicha_discard, tiles_136)

            return None, None

        return super(YakuhaiStrategy, self).try_to_call_meld(tile, is_kamicha_discard, tiles_136)

    def _is_yakuhai_pon(self, meld):
        return meld.type == Meld.PON and meld.tiles[0] // 4 in self.player.valued_honors
