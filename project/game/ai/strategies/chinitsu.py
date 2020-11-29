from game.ai.strategies.honitsu import HonitsuStrategy
from game.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter
from mahjong.utils import count_tiles_by_suits, is_honor, is_man, is_pin, is_sou, is_tile_strictly_isolated, plus_dora


class ChinitsuStrategy(BaseStrategy):
    min_shanten = 4

    chosen_suit = None

    dora_count_suitable = 0
    dora_count_not_suitable = 0

    def get_open_hand_han(self):
        return 5

    def should_activate_strategy(self, tiles_136, meld_tile=None):
        """
        We can go for chinitsu strategy if we have prevalence of one suit
        """

        result = super(ChinitsuStrategy, self).should_activate_strategy(tiles_136)
        if not result:
            return False

        # when making decisions about chinitsu, we should consider
        # the state of our own hand,
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        suits = count_tiles_by_suits(tiles_34)

        suits = [x for x in suits if x["name"] != "honor"]
        suits = sorted(suits, key=lambda x: x["count"], reverse=True)
        suit = suits[0]

        count_of_shuntsu_other_suits = 0
        count_of_koutsu_other_suits = 0

        count_of_shuntsu_other_suits += HonitsuStrategy._count_of_shuntsu(tiles_34, suits[1]["function"])
        count_of_shuntsu_other_suits += HonitsuStrategy._count_of_shuntsu(tiles_34, suits[2]["function"])

        count_of_koutsu_other_suits += HonitsuStrategy._count_of_koutsu(tiles_34, suits[1]["function"])
        count_of_koutsu_other_suits += HonitsuStrategy._count_of_koutsu(tiles_34, suits[2]["function"])

        # we need to have at least 9 tiles of one suit to fo for chinitsu
        if suit["count"] < 9:
            return False

        # here we only check doras in different suits, we will deal
        # with honors later
        self._initialize_chinitsu_dora_count(tiles_136, suit)

        # 3 non-isolated doras in other suits is too much
        # to even try
        if self.dora_count_not_suitable >= 3:
            return False

        if self.dora_count_not_suitable == 2:
            # 2 doras in other suits, no doras in our suit
            # let's not consider chinitsu
            if self.dora_count_suitable == 0:
                return False

            # we have 2 doras in other suits and we
            # are 1 shanten, let's not rush chinitsu
            if self.player.ai.shanten == 1:
                return False

            # too late to get rid of doras in other suits
            if self.player.round_step > 8:
                return False

        # we are almost tempai, chinitsu is slower
        if suit["count"] == 9 and self.player.ai.shanten == 1:
            return False

        # only 10 tiles by 9th turn is too slow, considering alternative
        if suit["count"] == 10 and self.player.ai.shanten == 1 and self.player.round_step > 8:
            return False

        # only 11 tiles or less by 12th turn is too slow, considering alternative
        if suit["count"] <= 11 and self.player.round_step > 11:
            return False

        # if we have a pon of honors, let's not go for chinitsu
        honor_pons = len([x for x in range(0, 34) if is_honor(x) and tiles_34[x] >= 3])
        if honor_pons >= 1:
            return False

        # if we have a valued pair, let's not go for chinitsu
        valued_pairs = len([x for x in self.player.valued_honors if tiles_34[x] == 2])
        if valued_pairs >= 1:
            return False

        # if we have a pair of honor doras, let's not go for chinitsu
        honor_doras_pairs = len(
            [
                x
                for x in range(0, 34)
                if is_honor(x) and tiles_34[x] == 2 and plus_dora(x * 4, self.player.table.dora_indicators)
            ]
        )
        if honor_doras_pairs >= 1:
            return False

        # if we have a honor pair, we will only throw them away if it's early in the game
        # and if we have lots of tiles in our suit
        honor_pairs = len([x for x in range(0, 34) if is_honor(x) and tiles_34[x] == 2])
        if honor_pairs >= 2:
            return False
        if honor_pairs == 1:
            if suit["count"] < 11:
                return False
            if self.player.round_step > 8:
                return False

        # if we have a complete set in other suits, we can only throw it away if it's early in the game
        if count_of_shuntsu_other_suits + count_of_koutsu_other_suits >= 1:
            # too late to throw away chi after 8 step
            if self.player.round_step > 8:
                return False

            # already 1 shanten, no need to throw away complete set
            if self.player.round_step > 5 and self.player.ai.shanten == 1:
                return False

            # dora is not isolated and we have a complete set, let's not go for chinitsu
            if self.dora_count_not_suitable >= 1:
                return False

        self.chosen_suit = suit["function"]

        return True

    def is_tile_suitable(self, tile):
        """
        We can use only tiles of chosen suit and honor tiles
        :param tile: 136 tiles format
        :return: True
        """
        tile //= 4
        return self.chosen_suit(tile)

    def _initialize_chinitsu_dora_count(self, tiles_136, suit):
        tiles_34 = TilesConverter.to_34_array(tiles_136)

        dora_count_man = 0
        dora_count_man_not_isolated = 0
        dora_count_pin = 0
        dora_count_pin_not_isolated = 0
        dora_count_sou = 0
        dora_count_sou_not_isolated = 0

        for tile_136 in tiles_136:
            tile_34 = tile_136 // 4

            dora_count = plus_dora(
                tile_136, self.player.table.dora_indicators, add_aka_dora=self.player.table.has_aka_dora
            )

            if is_man(tile_34):
                dora_count_man += dora_count
                if not is_tile_strictly_isolated(tiles_34, tile_34):
                    dora_count_man_not_isolated += dora_count

            if is_pin(tile_34):
                dora_count_pin += dora_count
                if not is_tile_strictly_isolated(tiles_34, tile_34):
                    dora_count_pin_not_isolated += dora_count

            if is_sou(tile_34):
                dora_count_sou += dora_count
                if not is_tile_strictly_isolated(tiles_34, tile_34):
                    dora_count_sou_not_isolated += dora_count

        if suit["name"] == "pin":
            self.dora_count_suitable = dora_count_pin
            self.dora_count_not_suitable = dora_count_man_not_isolated + dora_count_sou_not_isolated
        elif suit["name"] == "sou":
            self.dora_count_suitable = dora_count_sou
            self.dora_count_not_suitable = dora_count_man_not_isolated + dora_count_pin_not_isolated
        elif suit["name"] == "man":
            self.dora_count_suitable = dora_count_man
            self.dora_count_not_suitable = dora_count_sou_not_isolated + dora_count_pin_not_isolated
