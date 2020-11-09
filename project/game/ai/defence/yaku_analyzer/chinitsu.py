from game.ai.defence.yaku_analyzer.yaku_analyzer import YakuAnalyzer
from mahjong.tile import TilesConverter
from mahjong.utils import count_tiles_by_suits, is_honor


class ChinitsuAnalyzer(YakuAnalyzer):
    id = "chinitsu"
    chosen_suit = None

    MIN_DISCARD = 5
    MIN_DISCARD_FOR_LESS_SUIT = 10
    MAX_MELDS = 3
    EARLY_DISCARD_DIVISOR = 3
    LESS_SUIT_PERCENTAGE_BORDER = 30

    def __init__(self, enemy):
        self.enemy = enemy
        self.chosen_suit = None

    def serialize(self):
        return {"id": self.id, "chosen_suit": self.chosen_suit and self.chosen_suit.__name__}

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
            elif suit != current_suit:
                return False

        assert current_suit

        # now let's check the following considiton:
        # if enemy had discarded tiles from that suit and after that he had discarded a tile from a different
        # suit from his hand - let's believe it's not chinitsu
        suit_discards_positions = [
            self.enemy.discards.index(x) for x in self.enemy.discards if current_suit["function"](x.value // 4)
        ]
        if suit_discards_positions:
            # we consider second discard of chosen suit to be reference point
            # first one could have happened when player was not yet sure if he is going to honitsu
            # after the second one there should be no discars of other suit from hand
            reference_discard = suit_discards_positions[min(1, len(suit_discards_positions) - 1)]
            discards_after = self.enemy.discards[reference_discard:]
            if discards_after:
                has_discarded_other_suit_from_hand = [
                    x.value
                    for x in discards_after
                    if (
                        not x.is_tsumogiri and not is_honor(x.value // 4) and not current_suit["function"](x.value // 4)
                    )
                ]
                if has_discarded_other_suit_from_hand:
                    return False

            # if we started discards suit tiles early, it's probably not chinitsu
            if suit_discards_positions[0] <= total_discards / ChinitsuAnalyzer.EARLY_DISCARD_DIVISOR:
                return False

        # finally let's check if discard is not too full of chosen suit
        if total_discards >= ChinitsuAnalyzer.MIN_DISCARD_FOR_LESS_SUIT:
            discards = [x.value for x in self.enemy.discards]
            discards_34 = TilesConverter.to_34_array(discards)
            result = count_tiles_by_suits(discards_34)

            suits = [x for x in result if x["name"] != "honor"]
            suits = sorted(suits, key=lambda x: x["count"], reverse=False)

            # not really suspicious
            less_suit = suits[0]
            less_suit_tiles = less_suit["count"]
            if less_suit != current_suit:
                return False

            percentage_of_less_suit = (less_suit_tiles / total_discards) * 100
            if percentage_of_less_suit > ChinitsuAnalyzer.LESS_SUIT_PERCENTAGE_BORDER:
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

    def get_tempai_probability_modifier(self):
        # if enemy has not yet discarded his suit and there are less than 3 melds, consider tempai less probable
        suit_discards = [x for x in self.enemy.discards if self.chosen_suit(x.value // 4)]

        if not suit_discards and len(self.enemy.melds):
            return 0.5

        return 1

    @staticmethod
    # FIXME: remove this method and use proper one from mahjong lib
    def _get_tile_suit(tile_136):
        suits = sorted(
            count_tiles_by_suits(TilesConverter.to_34_array([tile_136])), key=lambda x: x["count"], reverse=True
        )
        suit = suits[0]
        assert suit["count"] == 1
        return suit
