# -*- coding: utf-8 -*-
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter
from mahjong.utils import is_sou, is_pin, is_man, is_honor


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

    def determine_what_to_discard(self, closed_hand, outs_results, shanten, for_open_hand):
        """
        In honitsu mode we should discard tiles from other suit,
        even if it is better to save them
        """
        for i in closed_hand:
            i //= 4

            if not self.is_tile_suitable(i * 4):
                item_was_found = False
                for j in outs_results:
                    if j['discard'] == i:
                        item_was_found = True
                        j['tiles_count'] = 0
                        j['waiting'] = []

                if not item_was_found:
                    outs_results.append({
                        'discard': i,
                        'tiles_count': 1,
                        'waiting': []
                    })

        outs_results = sorted(outs_results, key=lambda x: x['tiles_count'], reverse=True)
        outs_results = sorted(outs_results, key=lambda x: self.is_tile_suitable(x['discard'] * 4), reverse=False)

        return super(HonitsuStrategy, self).determine_what_to_discard(closed_hand, outs_results, shanten, for_open_hand)
