# -*- coding: utf-8 -*-
from analytics.cases.main import ProcessDataCase
from analytics.tags import AGARI_TAG
from mahjong.tile import TilesConverter


class HonitsuHands(ProcessDataCase):
    HONITSU_ID = 34

    def process(self):
        self.load_all_records()
        filtered = self.filter_hands()
        for item in filtered:
            meld_tiles = []
            if item.parsed_melds:
                for meld in item.parsed_melds:
                    tiles = meld.tiles
                    if meld.type == meld.KAN or meld.type == meld.CHAKAN:
                        tiles = tiles[:3]
                    meld_tiles.extend(tiles)

            closed_hand_tiles = [int(x) for x in item.closed_hand.split(',')]
            tiles = closed_hand_tiles + meld_tiles
            print(TilesConverter.to_one_line_string(tiles))

    def filter_hands(self):
        filtered = []
        for hanchan in self.hanchans:
            for tag in hanchan.tags:
                if tag.tag_name == AGARI_TAG:
                    if self.HONITSU_ID in tag.parsed_yaku:
                        filtered.append(tag)
        return filtered
