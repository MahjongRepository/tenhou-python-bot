# -*- coding: utf-8 -*-
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter
from mahjong.utils import is_sou, is_pin, is_man, is_honor, simplify


class HonitsuStrategy(BaseStrategy):
    REQUIRED_TILES = 10

    chosen_suit = None

    def should_activate_strategy(self):
        """
        We can go for honitsu/chinitsu strategy if we have prevalence of one suit and honor tiles
        :return: boolean
        """

        result = super(HonitsuStrategy, self).should_activate_strategy()
        if not result:
            return False

        suits = [
            {'count': 0, 'name': 'sou', 'function': is_sou},
            {'count': 0, 'name': 'man', 'function': is_man},
            {'count': 0, 'name': 'pin', 'function': is_pin},
            {'count': 0, 'name': 'honor', 'function': is_honor}
        ]

        tiles = TilesConverter.to_34_array(self.player.tiles)
        for x in range(0, 34):
            tile = tiles[x]
            if not tile:
                continue

            for item in suits:
                if item['function'](x):
                    item['count'] += tile

        honor = [x for x in suits if x['name'] == 'honor'][0]
        suits = [x for x in suits if x['name'] != 'honor']
        suits = sorted(suits, key=lambda x: x['count'], reverse=True)

        suit = suits[0]
        count_of_pairs = 0
        for x in range(0, 34):
            if tiles[x] >= 2:
                count_of_pairs += 1

        suits.remove(suit)
        count_of_ryanmens = self._find_ryanmen_waits(tiles, suits[0]['function'])
        count_of_ryanmens += self._find_ryanmen_waits(tiles, suits[1]['function'])

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
