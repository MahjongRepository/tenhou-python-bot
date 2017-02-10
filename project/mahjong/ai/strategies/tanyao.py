# -*- coding: utf-8 -*-
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.constants import TERMINAL_INDICES, HONOR_INDICES
from mahjong.tile import TilesConverter
from mahjong.utils import is_sou, is_pin, is_man, is_honor


class TanyaoStrategy(BaseStrategy):
    min_shanten = 3
    not_suitable_tiles = TERMINAL_INDICES + HONOR_INDICES

    def should_activate_strategy(self):
        """
        Tanyao hand is a hand without terminal and honor tiles, to achieve this
        we will use different approaches
        :return: boolean
        """

        result = super(TanyaoStrategy, self).should_activate_strategy()
        if not result:
            return False

        tiles = TilesConverter.to_34_array(self.player.tiles)
        count_of_terminal_pon_sets = 0
        count_of_terminal_pairs = 0
        count_of_valued_pairs = 0
        for x in range(0, 34):
            tile = tiles[x]
            if not tile:
                continue

            if x in self.not_suitable_tiles and tile == 3:
                count_of_terminal_pon_sets += 1

            if x in self.not_suitable_tiles and tile == 2:
                count_of_terminal_pairs += 1

                if x in self.player.ai.valued_honors:
                    count_of_valued_pairs += 1

        # if we already have pon of honor\terminal tiles
        # we don't need to open hand for tanyao
        if count_of_terminal_pon_sets > 0:
            return False

        # with valued pair (yakuhai wind or dragon)
        # we don't need to go for tanyao
        if count_of_valued_pairs > 0:
            return False

        # one pair is ok in tanyao pair
        # but 2+ pairs can't be suitable
        if count_of_terminal_pairs > 1:
            return False

        # 123 and 789 indices
        indices = [
            [0, 1, 2], [6, 7, 8],
            [9, 10, 11], [15, 16, 17],
            [18, 19, 20], [24, 25, 26]
        ]

        for index_set in indices:
            first = tiles[index_set[0]]
            second = tiles[index_set[1]]
            third = tiles[index_set[2]]
            if first >= 1 and second >= 1 and third >= 1:
                return False

        return True

    def is_tile_suitable(self, tile):
        """
        We can use only simples tiles (2-8) in any suit
        :param tile: 136 tiles format
        :return: True
        """
        tile //= 4
        return tile not in self.not_suitable_tiles
