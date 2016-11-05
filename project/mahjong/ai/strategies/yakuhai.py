# -*- coding: utf-8 -*-
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter


class YakuhaiStrategy(BaseStrategy):

    def should_activate_strategy(self):
        """
        We can go for yakuhai strategy if we have at least one yakuhai pair in the hand
        :return: boolean
        """
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        return any([tiles_34[x] >= 2 for x in self.player.ai.valued_honors])

    def is_tile_suitable(self, tile):
        """
        For yakuhai we don't have limits
        :param tile: 136 tiles format
        :return: True
        """
        return True
