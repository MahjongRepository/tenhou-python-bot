# -*- coding: utf-8 -*-
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.meld import Meld
from mahjong.tile import TilesConverter


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
        has_valued_pairs = any([tiles_34[x] >= 2 for x in self.player.ai.valued_honors])
        return has_valued_pairs

    def is_tile_suitable(self, tile):
        """
        For yakuhai we don't have any limits
        :param tile: 136 tiles format
        :return: True
        """
        return True

    def determine_what_to_discard(self, closed_hand, outs_results, shanten, for_open_hand, tile_for_open_hand):
        if tile_for_open_hand:
            tile_for_open_hand //= 4

        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        valued_pairs = [x for x in self.player.ai.valued_honors if tiles_34[x] == 2]

        # when we trying to open hand with tempai state, we need to chose a valued pair waiting
        if shanten == 0 and valued_pairs and for_open_hand and tile_for_open_hand not in valued_pairs:
            valued_pair = valued_pairs[0]

            results = []
            for item in outs_results:
                if valued_pair in item.waiting:
                    results.append(item)
            return results
        else:
            return super(YakuhaiStrategy, self).determine_what_to_discard(closed_hand,
                                                                          outs_results,
                                                                          shanten,
                                                                          for_open_hand,
                                                                          tile_for_open_hand)

    def meld_had_to_be_called(self, tile):
        # for closed hand we don't need to open hand with special conditions
        if not self.player.is_open_hand:
            return False

        tile //= 4
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        valued_pairs = [x for x in self.player.ai.valued_honors if tiles_34[x] == 2]

        for meld in self.player.melds:
            # we have already opened yakuhai pon
            # so we don't need to open hand without shanten improvement
            if meld.type == Meld.PON and meld.tiles[0] // 4 in self.player.ai.valued_honors:
                return False

        # open hand for valued pon
        for valued_pair in valued_pairs:
            if valued_pair == tile:
                return True

        return False

