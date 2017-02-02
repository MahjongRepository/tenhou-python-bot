# -*- coding: utf-8 -*-
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter


class YakuhaiStrategy(BaseStrategy):

    def should_activate_strategy(self):
        """
        We can go for yakuhai strategy if we have at least one yakuhai pair in the hand,
        but with 5+ pairs in hand we don't need to go for yakuhai
        :return: boolean
        """
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        count_of_pairs = len([x for x in range(0, 34) if tiles_34[x] >= 2])
        has_valued_pairs = any([tiles_34[x] >= 2 for x in self.player.ai.valued_honors])
        return has_valued_pairs and count_of_pairs < 4

    def is_tile_suitable(self, tile):
        """
        For yakuhai we don't have limits
        :param tile: 136 tiles format
        :return: True
        """
        return True

    def determine_what_to_discard(self, closed_hand, outs_results, shanten):
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        valued_pairs = [x for x in self.player.ai.valued_honors if tiles_34[x] == 2]

        if shanten == 0 and valued_pairs:
            valued_pair = valued_pairs[0]

            tile_to_discard = None
            for item in outs_results:
                if valued_pair in item['waiting']:
                    tile_to_discard = item['discard']
            tile_to_discard = TilesConverter.find_34_tile_in_136_array(tile_to_discard, closed_hand)
            return tile_to_discard
        else:
            return super(YakuhaiStrategy, self).determine_what_to_discard(closed_hand, outs_results, shanten)
