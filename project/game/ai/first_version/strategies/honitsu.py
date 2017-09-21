# -*- coding: utf-8 -*-
from mahjong.tile import TilesConverter
from mahjong.utils import count_tiles_by_suits, is_honor, simplify

from game.ai.first_version.strategies.main import BaseStrategy


class HonitsuStrategy(BaseStrategy):
    REQUIRED_TILES = 10
    min_shanten = 4

    chosen_suit = None

    def should_activate_strategy(self):
        """
        We can go for honitsu/chinitsu strategy if we have prevalence of one suit and honor tiles
        :return: boolean
        """

        result = super(HonitsuStrategy, self).should_activate_strategy()
        if not result:
            return False

        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        suits = count_tiles_by_suits(tiles_34)

        honor = [x for x in suits if x['name'] == 'honor'][0]
        suits = [x for x in suits if x['name'] != 'honor']
        suits = sorted(suits, key=lambda x: x['count'], reverse=True)

        suit = suits[0]
        count_of_pairs = 0
        for x in range(0, 34):
            if tiles_34[x] >= 2:
                count_of_pairs += 1

        suits.remove(suit)
        count_of_ryanmens = self._find_ryanmen_waits(tiles_34, suits[0]['function'])
        count_of_ryanmens += self._find_ryanmen_waits(tiles_34, suits[1]['function'])

        # it is a bad idea go for honitsu with ryanmen in other suit
        if count_of_ryanmens > 0 and not self.player.is_open_hand:
            return False

        # we need to have prevalence of one suit and completed forms in the hand
        # for now let's check only pairs in the hand
        # TODO check ryanmen forms as well and honor tiles count
        if suit['count'] + honor['count'] >= HonitsuStrategy.REQUIRED_TILES:
            self.chosen_suit = suit['function']
            return count_of_pairs > 0
        else:
            return False

    def is_tile_suitable(self, tile):
        """
        We can use only tiles of chosen suit and honor tiles
        :param tile: 136 tiles format
        :return: True
        """
        tile //= 4
        return self.chosen_suit(tile) or is_honor(tile)

    def _find_ryanmen_waits(self, tiles, suit):
        suit_tiles = []
        for x in range(0, 34):
            tile = tiles[x]
            if not tile:
                continue

            if suit(x):
                suit_tiles.append(x)

        count_of_ryanmen_waits = 0
        simple_tiles = [simplify(x) for x in suit_tiles]
        for x in range(0, len(simple_tiles)):
            tile = simple_tiles[x]
            # we cant build ryanmen with 1 and 9
            if tile == 1 or tile == 9:
                continue

            # bordered tile
            if x + 1 == len(simple_tiles):
                continue

            if tile + 1 == simple_tiles[x + 1]:
                count_of_ryanmen_waits += 1

        return count_of_ryanmen_waits
