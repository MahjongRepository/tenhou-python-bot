# -*- coding: utf-8 -*-
from mahjong.ai.strategies.main import BaseStrategy
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

    def determine_what_to_discard(self, closed_hand, outs_results, shanten, for_open_hand):
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        valued_pairs = [x for x in self.player.ai.valued_honors if tiles_34[x] == 2]

        # when we trying to open hand with tempai state, we need to chose a valued pair waiting
        if shanten == 0 and valued_pairs and for_open_hand:
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
                                                                          for_open_hand)
