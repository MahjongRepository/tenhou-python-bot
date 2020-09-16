from mahjong.constants import HONOR_INDICES
from mahjong.tile import TilesConverter
from mahjong.utils import count_tiles_by_suits


class HonitsuAnalyzer:
    id = "Honitsu"

    def __init__(self, player):
        self.player = player

        self.chosen_suit = None

    def is_yaku_active(self):
        self.chosen_suit = self._get_chosen_suit_from_discards()
        return self.chosen_suit and True or False

    def melds_han(self):
        return self.player.is_open_hand and 2 or 3

    def get_dangerous_tiles(self):
        if not self.chosen_suit:
            return []

        dangerous_tiles = HONOR_INDICES[:]
        for x in range(0, 34):
            if self.chosen_suit(x):
                dangerous_tiles.append(x)

        return dangerous_tiles

    def _get_chosen_suit_from_discards(self):
        """
        Check that user opened all sets with same suit
        :return: None or chosen suit function
        """
        discards = [x.value for x in self.player.discards]
        discards_34 = TilesConverter.to_34_array(discards)
        total_discards = sum(discards_34)

        # there is no sense to analyze earlier discards
        if total_discards < 6:
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
        if percentage_of_less_suit <= 20 and percentage_of_honor_tiles <= 30:
            return suits[0]["function"]

        return None
