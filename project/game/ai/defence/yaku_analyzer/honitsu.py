from game.ai.defence.yaku_analyzer.chinitsu import ChinitsuAnalyzer
from game.ai.defence.yaku_analyzer.honitsu_analyzer_base import HonitsuAnalyzerBase
from game.ai.helpers.defence import TileDanger
from mahjong.tile import TilesConverter
from mahjong.utils import count_tiles_by_suits, is_honor


class HonitsuAnalyzer(HonitsuAnalyzerBase):
    id = "honitsu"

    MIN_DISCARD = 6
    MAX_MELDS = 3
    EARLY_DISCARD_DIVISOR = 4
    LESS_SUIT_PERCENTAGE_BORDER = 20
    HONORS_PERCENTAGE_BORDER = 30

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
            elif suit["name"] != current_suit["name"]:
                return False

        # let's check discards
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
            if not current_suit:
                current_suit = less_suit
            elif current_suit != less_suit:
                return False

        # still cannot determine the suit - this is probably not honitsu
        if not current_suit:
            return False

        if not self._check_discard_order(current_suit, int(total_discards / HonitsuAnalyzer.EARLY_DISCARD_DIVISOR)):
            return False

        # all checks have passed - assume this is honitsu
        self.chosen_suit = current_suit["function"]
        return True

    def melds_han(self):
        return self.enemy.is_open_hand and 2 or 3

    def get_safe_tiles_34(self):
        if not self.chosen_suit:
            return []

        safe_tiles = []
        for x in range(0, 34):
            if not self.chosen_suit(x) and not is_honor(x):
                safe_tiles.append(x)

        return safe_tiles

    def get_bonus_danger(self, tile_136, number_of_revealed_tiles):
        tile_34 = tile_136 // 4

        if is_honor(tile_34):
            if number_of_revealed_tiles == 4:
                return []
            elif number_of_revealed_tiles == 3:
                return [TileDanger.HONITSU_THIRD_HONOR_BONUS_DANGER]
            elif number_of_revealed_tiles == 2:
                return [TileDanger.HONITSU_SECOND_HONOR_BONUS_DANGER]
            else:
                return [TileDanger.HONITSU_SHONPAI_HONOR_BONUS_DANGER]

        return []

    def is_absorbed(self, possible_yaku, tile_34=None):
        return self._is_absorbed_by(possible_yaku, ChinitsuAnalyzer.id, tile_34)
