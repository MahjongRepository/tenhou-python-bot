from game.ai.defence.yaku_analyzer.chinitsu import ChinitsuAnalyzer
from game.ai.defence.yaku_analyzer.yaku_analyzer import YakuAnalyzer
from game.ai.helpers.defence import TileDanger
from mahjong.constants import HONOR_INDICES
from mahjong.tile import TilesConverter
from mahjong.utils import count_tiles_by_suits, is_honor


class HonitsuAnalyzer(YakuAnalyzer):
    id = "honitsu"
    chosen_suit = None

    MIN_DISCARD = 6
    MAX_MELDS = 3
    EARLY_DISCARD_DIVISOR = 4
    LESS_SUIT_PERCENTAGE_BORDER = 20
    HONORS_PERCENTAGE_BORDER = 30

    def __init__(self, enemy):
        self.enemy = enemy
        self.chosen_suit = None

    def serialize(self):
        return {"id": self.id, "chosen_suit": self.chosen_suit and self.chosen_suit.__name__}

    def is_yaku_active(self):
        # TODO: in some distant future we may want to analyze menhon as well
        if not self.enemy.melds:
            return False

        total_melds = len(self.enemy.melds)
        total_discards = len(self.enemy.discards)

        # let's check if there is too little info to analyze
        if total_discards < HonitsuAnalyzer.MIN_DISCARD and total_melds < HonitsuAnalyzer.MAX_MELDS:
            return False

        # first of all - check melds, they must be all from one suit or honors
        current_suit = None
        for meld in self.enemy.melds:
            tile = meld.tiles[0]
            tile_34 = tile // 4

            if is_honor(tile_34):
                continue

            suit = ChinitsuAnalyzer._get_tile_suit(tile)
            if not current_suit:
                current_suit = suit
            elif suit != current_suit:
                return False

        # it is possible that we have only melded honor tiles, let's check discards in that case
        if not current_suit:
            discards = [x.value for x in self.enemy.discards]
            discards_34 = TilesConverter.to_34_array(discards)
            result = count_tiles_by_suits(discards_34)

            honors = [x for x in result if x["name"] == "honor"][0]
            suits = [x for x in result if x["name"] != "honor"]
            suits = sorted(suits, key=lambda x: x["count"], reverse=False)

            less_suit = suits[0]
            less_suit_tiles = less_suit["count"]
            percentage_of_less_suit = (less_suit_tiles / total_discards) * 100
            percentage_of_honor_tiles = (honors["count"] / total_discards) * 100

            # there is not too much one suit + honor tiles in the discard
            # so we can tell that user trying to collect honitsu
            if (
                percentage_of_less_suit <= HonitsuAnalyzer.LESS_SUIT_PERCENTAGE_BORDER
                and percentage_of_honor_tiles <= HonitsuAnalyzer.HONORS_PERCENTAGE_BORDER
            ):
                current_suit = less_suit

        # still cannot determine the suit - this is probably not honitsu
        if not current_suit:
            return False

        # now let's check the following considiton:
        # if enemy had discarded tiles from that suit or honor and after that he had discarded a tile from a different
        # suit from his hand - let's believe it's not honitsu
        suit_discards_positions = [
            self.enemy.discards.index(x)
            for x in self.enemy.discards
            if ChinitsuAnalyzer._is_tile_from_suit(current_suit, x.value)
        ]
        if suit_discards_positions:
            last_honitsu_discard = suit_discards_positions[-1]
            discards_after = self.enemy.discards[last_honitsu_discard:]
            if discards_after:
                has_discarded_other_suit_from_hand = [
                    x
                    for x in discards_after
                    if (
                        not x.is_tsumogiri
                        and not is_honor(x.value // 4)
                        and not ChinitsuAnalyzer._is_tile_from_suit(current_suit, x.value)
                    )
                ]
                if has_discarded_other_suit_from_hand:
                    return False

            # if we started discards suit tiles early, it's probably not honitsu
            if suit_discards_positions[0] <= total_discards / HonitsuAnalyzer.EARLY_DISCARD_DIVISOR:
                return False

        # all checks have passed - assume this is honitsu
        self.chosen_suit = current_suit["function"]
        return True

    def melds_han(self):
        return self.enemy.is_open_hand and 2 or 3

    def get_safe_tiles_34(self):
        if not self.chosen_suit:
            return []

        safe_tiles = HONOR_INDICES[:]
        for x in range(0, 34):
            if not self.chosen_suit(x):
                safe_tiles.append(x)

        return safe_tiles

    def get_bonus_danger(self, tile_136, number_of_revealed_tiles):
        tile_34 = tile_136 // 4

        if is_honor(tile_34):
            if number_of_revealed_tiles == 4:
                return []
            elif number_of_revealed_tiles == 3:
                return [TileDanger.HONITSU_THIRD_HONOR_BONUS_DANGER]
            else:
                return [TileDanger.HONITSU_FIRST_SECOND_HONOR_BONUS_DANGER]

        return []
