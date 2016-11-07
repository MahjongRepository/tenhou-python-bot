# -*- coding: utf-8 -*-
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter
from mahjong.utils import is_sou, is_pin, is_man, is_honor


class HonitsuStrategy(BaseStrategy):
    chosen_suit = None

    def should_activate_strategy(self):
        """
        We can go for honitsu/chinitsu strategy if we have prevalence of one suit and honor tiles
        :return: boolean
        """

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

        if suit['count'] + honor['count'] >= 9:
            self.chosen_suit = suit['function']
            return True
        else:
            return False

    def is_tile_suitable(self, tile):
        """
        We can use only tiles of chosen suit and honor tiles
        :param tile: 136 tiles format
        :return: True
        """
        return self.chosen_suit(tile // 4) or is_honor(tile // 4)
