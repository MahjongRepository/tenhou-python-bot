from game.ai.defence.yaku_analyzer.honitsu_analyzer_base import HonitsuAnalyzerBase
from mahjong.tile import TilesConverter
from mahjong.utils import count_tiles_by_suits, is_honor


class ChinitsuAnalyzer(HonitsuAnalyzerBase):
    id = "chinitsu"

    MIN_DISCARD = 5
    MIN_DISCARD_FOR_LESS_SUIT = 10
    MAX_MELDS = 3
    EARLY_DISCARD_DIVISOR = 3
    LESS_SUIT_PERCENTAGE_BORDER = 30

    def is_yaku_active(self):
        # TODO: in some distant future we may want to analyze menchin as well
        if not self.enemy.melds:
            return False

        total_melds = len(self.enemy.melds)
        total_discards = len(self.enemy.discards)

        # let's check if there is too little info to analyze
        if total_discards < ChinitsuAnalyzer.MIN_DISCARD and total_melds < ChinitsuAnalyzer.MAX_MELDS:
            return False

        # first of all - check melds, they must be all from one suit
        current_suit = None
        for meld in self.enemy.melds:
            tile = meld.tiles[0]
            tile_34 = tile // 4

            if is_honor(tile_34):
                return False

            suit = self._get_tile_suit(tile)
            if not current_suit:
                current_suit = suit
            elif suit["name"] != current_suit["name"]:
                return False

        assert current_suit

        if not self._check_discard_order(current_suit, int(total_discards / ChinitsuAnalyzer.EARLY_DISCARD_DIVISOR)):
            return False

        # finally let's check if discard is not too full of chosen suit

        discards = [x.value for x in self.enemy.discards]
        discards_34 = TilesConverter.to_34_array(discards)
        result = count_tiles_by_suits(discards_34)

        suits = [x for x in result if x["name"] != "honor"]
        suits = sorted(suits, key=lambda x: x["count"], reverse=False)

        less_suits = [x for x in suits if x["count"] == suits[0]["count"]]
        assert len(less_suits) != 0

        current_suit_is_less_suit = False
        for less_suit in less_suits:
            if less_suit["name"] == current_suit["name"]:
                current_suit_is_less_suit = True

        if not current_suit_is_less_suit:
            return False

        less_suit = suits[0]
        less_suit_tiles = less_suit["count"]

        if total_discards >= ChinitsuAnalyzer.MIN_DISCARD_FOR_LESS_SUIT:
            percentage_of_less_suit = (less_suit_tiles / total_discards) * 100
            if percentage_of_less_suit > ChinitsuAnalyzer.LESS_SUIT_PERCENTAGE_BORDER:
                return False
        else:
            if len(self.enemy.melds) < 2:
                return False

            if less_suit_tiles > 1:
                return False

        self.chosen_suit = current_suit["function"]
        return True

    def melds_han(self):
        return self.enemy.is_open_hand and 5 or 6

    def get_safe_tiles_34(self):
        if not self.chosen_suit:
            return []

        safe_tiles = []
        for x in range(0, 34):
            if not self.chosen_suit(x):
                safe_tiles.append(x)

        return safe_tiles

    @staticmethod
    # FIXME: remove this method and use proper one from mahjong lib
    def _get_tile_suit(tile_136):
        suits = sorted(
            count_tiles_by_suits(TilesConverter.to_34_array([tile_136])), key=lambda x: x["count"], reverse=True
        )
        suit = suits[0]
        assert suit["count"] == 1
        return suit
