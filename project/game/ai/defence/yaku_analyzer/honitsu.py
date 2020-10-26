from mahjong.constants import HONOR_INDICES
from mahjong.tile import TilesConverter
from mahjong.utils import count_tiles_by_suits, is_honor


class HonitsuAnalyzer:
    id = "honitsu"
    chosen_suit = None

    MIN_DISCARD = 6
    LESS_SUIT_PERCENTAGE_BORDER = 20
    HONORS_PERCENTAGE_BORDER = 30

    def __init__(self, player):
        self.player = player
        self.chosen_suit = None

    def serialize(self):
        return {"id": self.id, "chosen_suit": self.chosen_suit and self.chosen_suit.__name__}

    def is_yaku_active(self):
        self.chosen_suit = self._get_chosen_suit_from_discards()
        if not self.chosen_suit:
            return False

        all_melds_from_chosen_suit = True
        for meld in self.player.melds:
            tile = meld.tiles[0]
            tile_34 = tile // 4
            if is_honor(tile_34):
                continue

            all_melds_from_chosen_suit &= self.chosen_suit(tile_34)

        return all_melds_from_chosen_suit

    def melds_han(self):
        return self.player.is_open_hand and 2 or 3

    def get_safe_tiles_34(self):
        if not self.chosen_suit:
            return []

        safe_tiles = HONOR_INDICES[:]
        for x in range(0, 34):
            if not self.chosen_suit(x):
                safe_tiles.append(x)

        return safe_tiles

    def _get_chosen_suit_from_discards(self):
        """
        Check that user opened all sets with same suit
        :return: None or chosen suit function
        """
        discards = [x.value for x in self.player.discards]
        discards_34 = TilesConverter.to_34_array(discards)
        total_discards = sum(discards_34)

        # there is no sense to analyze earlier discards
        if total_discards < HonitsuAnalyzer.MIN_DISCARD:
            return None

        result = count_tiles_by_suits(discards_34)

        honors = [x for x in result if x["name"] == "honor"][0]
        suits = [x for x in result if x["name"] != "honor"]
        suits = sorted(suits, key=lambda x: x["count"], reverse=False)

        less_suit = suits[0]["count"]
        percentage_of_less_suit = (less_suit / total_discards) * 100
        percentage_of_honor_tiles = (honors["count"] / total_discards) * 100

        # there is not too much one suit + honor tiles in the discard
        # so we can tell that user trying to collect honitsu
        if (
            percentage_of_less_suit <= HonitsuAnalyzer.LESS_SUIT_PERCENTAGE_BORDER
            and percentage_of_honor_tiles <= HonitsuAnalyzer.HONORS_PERCENTAGE_BORDER
        ):
            return suits[0]["function"]

        return None
