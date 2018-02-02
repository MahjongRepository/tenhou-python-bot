# -*- coding: utf-8 -*-
from mahjong.meld import Meld
from mahjong.tile import TilesConverter

from game.ai.first_version.strategies.main import BaseStrategy


class YakuhaiStrategy(BaseStrategy):

    def should_activate_strategy(self):
        """
        We can go for yakuhai strategy if we have at least one yakuhai pair in the hand
        :return: boolean
        """
        result = super(YakuhaiStrategy, self).should_activate_strategy()
        if not result:
            return False

        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        valued_pairs = [x for x in self.player.valued_honors if tiles_34[x] >= 2]

        for pair in valued_pairs:
            # we have valued pair in the hand and there is enough tiles
            # in the wall
            if self.player.total_tiles(pair, tiles_34) < 4:
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
            if self.player.ai.previous_shanten >= 1:
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

    def _is_yakuhai_pon(self, meld):
        return meld.type == Meld.PON and meld.tiles[0] // 4 in self.player.valued_honors
