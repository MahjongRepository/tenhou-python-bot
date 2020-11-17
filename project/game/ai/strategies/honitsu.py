from game.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter
from mahjong.utils import (
    count_tiles_by_suits,
    is_honor,
    is_man,
    is_pin,
    is_sou,
    is_tile_strictly_isolated,
    plus_dora,
    simplify,
)


class HonitsuStrategy(BaseStrategy):
    min_shanten = 4

    chosen_suit = None

    tiles_count_our_suit = 0
    dora_count_our_suit = 0
    dora_count_other_suits_not_isolated = 0
    tiles_count_other_suits = 0
    tiles_count_other_suits_not_isolated = 0

    def get_open_hand_han(self):
        return 2

    def should_activate_strategy(self, tiles_136, meld_tile=None):
        """
        We can go for honitsu strategy if we have prevalence of one suit and honor tiles
        """

        result = super(HonitsuStrategy, self).should_activate_strategy(tiles_136)
        if not result:
            return False

        tiles_34 = TilesConverter.to_34_array(tiles_136)
        suits = count_tiles_by_suits(tiles_34)

        suits = [x for x in suits if x["name"] != "honor"]
        suits = sorted(suits, key=lambda x: x["count"], reverse=True)

        suit = suits[0]

        count_of_shuntsu_other_suits = 0
        count_of_koutsu_other_suits = 0
        count_of_ryanmen_other_suits = 0

        count_of_shuntsu_other_suits += self._count_of_shuntsu(tiles_34, suits[1]["function"])
        count_of_shuntsu_other_suits += self._count_of_shuntsu(tiles_34, suits[2]["function"])

        count_of_koutsu_other_suits += self._count_of_koutsu(tiles_34, suits[1]["function"])
        count_of_koutsu_other_suits += self._count_of_koutsu(tiles_34, suits[2]["function"])

        count_of_ryanmen_other_suits += self._find_ryanmen_waits(tiles_34, suits[1]["function"])
        count_of_ryanmen_other_suits += self._find_ryanmen_waits(tiles_34, suits[2]["function"])

        self._calculate_suitable_and_not_suitable_tiles_cnt(tiles_34, suit["function"])
        self._initialize_honitsu_dora_count(tiles_136, suit)

        # let's not go for honitsu if we have 5 or more tiles in other suits
        if self.tiles_count_other_suits >= 5:
            return False

        # 7th turn and still 4 tiles in other suits - meh
        if self.tiles_count_other_suits >= 4 and self.player.round_step > 6:
            return False

        # 12th turn is too late and we still have too many tiles in other suits
        if self.tiles_count_other_suits >= 3 and self.player.round_step > 11:
            return False

        # let's not go for honitsu if we have 2 or more non-isolated doras
        # in other suits
        if self.dora_count_other_suits_not_isolated >= 2:
            return False

        # if we have a pon of valued doras, let's not go for honitsu
        # we have a mangan anyway, let's go for fastest hand
        valued_pons = [x for x in self.player.valued_honors if tiles_34[x] >= 3]
        for pon in valued_pons:
            dora_count_valued_pons = plus_dora(pon * 4, self.player.table.dora_indicators)
            if dora_count_valued_pons > 0:
                return False

        valued_pairs = len([x for x in self.player.valued_honors if tiles_34[x] == 2])
        honor_pairs_or_pons = len([x for x in range(0, 34) if is_honor(x) and tiles_34[x] >= 2])
        honor_doras_pairs_or_pons = len(
            [
                x
                for x in range(0, 34)
                if is_honor(x) and tiles_34[x] >= 2 and plus_dora(x * 4, self.player.table.dora_indicators)
            ]
        )
        unvalued_singles = len(
            [x for x in range(0, 34) if is_honor(x) and x not in self.player.valued_honors and tiles_34[x] == 1]
        )

        # what's the point of honitsu if there is not a single honor pair
        if honor_pairs_or_pons == 0:
            return False

        # if we have twu ryanmens in other suits
        if count_of_ryanmen_other_suits >= 2:
            return False

        # let's not go for honitsu nomi
        if not valued_pairs and not valued_pons:
            # this is not honitsu, maybe it will be pinfu one day
            if self.tiles_count_our_suit <= 7 and honor_pairs_or_pons < 2:
                return False

            # also looks more like pinfu
            if self.tiles_count_other_suits >= 4:
                return False

            # so-so, let's just not go for honitsu nomi
            if self.tiles_count_our_suit <= 9 and honor_pairs_or_pons == 1:
                if not self.dora_count_our_suit and not honor_doras_pairs_or_pons:
                    return False

        # if we have some decent amount of not isolated tiles in other suits
        # we may not rush for honitsu considering other conditions
        if self.tiles_count_other_suits_not_isolated >= 3:
            # if we don't have pair or pon of honored doras
            if honor_doras_pairs_or_pons == 0:
                # if we have a ryanmen with dora in other suit and no honor doras, so let's not rush honitsu
                if count_of_ryanmen_other_suits >= 1 and self.dora_count_other_suits_not_isolated >= 1:
                    return False

                # we need to either have a valued pair or have at least two honor
                # pairs to consider honitsu
                if valued_pairs == 0 and honor_pairs_or_pons < 2:
                    return False

                # doesn't matter valued or not, if we have just one honor pair
                # and have some single unvalued tiles, let's throw them away
                # first
                if honor_pairs_or_pons == 1 and unvalued_singles >= 2:
                    return False

                # 3 non-isolated unsuitable tiles, 1-shanen and already 8th turn
                # let's not consider honitsu here
                if self.player.ai.shanten == 1 and self.player.round_step > 8:
                    return False
            else:
                # we have a pon of unvalued honor doras, but it looks like
                # it's faster to build our hand without honitsu
                if self.player.ai.shanten == 1:
                    return False

        # if we have a complete set in other suits, we can only throw it away if it's early in the game
        if count_of_shuntsu_other_suits + count_of_koutsu_other_suits >= 1:
            # too late to throw away chi after 5 step
            if self.player.round_step > 5:
                return False

            # already 1 shanten, no need to throw away complete set
            if self.player.ai.shanten == 1:
                return False

            # dora is not isolated and we have a complete set, let's not go for honitsu
            if self.dora_count_other_suits_not_isolated >= 1:
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
        return self.chosen_suit(tile) or is_honor(tile)

    def meld_had_to_be_called(self, tile):
        has_not_suitable_tiles = False

        for hand_tile in self.player.tiles:
            if not self.is_tile_suitable(hand_tile):
                has_not_suitable_tiles = True
                break

        # if we still have unsuitable tiles, let's call honor pons
        # even if they don't change number of shanten
        if has_not_suitable_tiles and is_honor(tile // 4):
            return True

        return False

    def _calculate_suitable_and_not_suitable_tiles_cnt(self, tiles_34, suit):
        self.tiles_count_other_suits = 0
        self.tiles_count_other_suits_not_isolated = 0

        for x in range(0, 34):
            tile_count = tiles_34[x]
            if not tile_count:
                continue

            if suit(x):
                self.tiles_count_our_suit += tile_count
            elif not is_honor(x):
                self.tiles_count_other_suits += tile_count
                if not is_tile_strictly_isolated(tiles_34, x):
                    self.tiles_count_other_suits_not_isolated += tile_count

    def _initialize_honitsu_dora_count(self, tiles_136, suit):
        tiles_34 = TilesConverter.to_34_array(tiles_136)

        dora_count_man = 0
        dora_count_pin = 0
        dora_count_sou = 0

        dora_count_man_not_isolated = 0
        dora_count_pin_not_isolated = 0
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
            self.dora_count_our_suit = dora_count_pin
            self.dora_count_other_suits_not_isolated = dora_count_man_not_isolated + dora_count_sou_not_isolated
        elif suit["name"] == "sou":
            self.dora_count_our_suit = dora_count_sou
            self.dora_count_other_suits_not_isolated = dora_count_man_not_isolated + dora_count_pin_not_isolated
        elif suit["name"] == "man":
            self.dora_count_our_suit = dora_count_man
            self.dora_count_other_suits_not_isolated = dora_count_sou_not_isolated + dora_count_pin_not_isolated

    @staticmethod
    def _find_ryanmen_waits(tiles, suit):
        suit_tiles = []
        for x in range(0, 34):
            tile = tiles[x]
            if not tile:
                continue

            if suit(x):
                suit_tiles.append(x)

        count_of_ryanmen_waits = 0
        simple_tiles = [simplify(x) for x in suit_tiles]
        for x in range(0, len(simple_tiles)):
            tile = simple_tiles[x]
            # we cant build ryanmen with 1 and 9
            if tile == 0 or tile == 8:
                continue

            # bordered tile
            if x + 1 == len(simple_tiles):
                continue

            if tile + 1 == simple_tiles[x + 1]:
                count_of_ryanmen_waits += 1

        return count_of_ryanmen_waits

    # we know we have no more that 5 tiles of other suit,
    # so this is a simplified version
    # be aware, that it will return 2 for 2345 form so use with care
    @staticmethod
    def _count_of_shuntsu(tiles, suit):
        suit_tiles = []
        for x in range(0, 34):
            tile = tiles[x]
            if not tile:
                continue

            if suit(x):
                suit_tiles.append(x)

        count_of_left_tiles = 0
        count_of_middle_tiles = 0
        count_of_right_tiles = 0

        simple_tiles = [simplify(x) for x in suit_tiles]
        for x in range(0, len(simple_tiles)):
            tile = simple_tiles[x]

            if tile + 1 in simple_tiles and tile + 2 in simple_tiles:
                count_of_left_tiles += 1

            if tile - 1 in simple_tiles and tile + 1 in simple_tiles:
                count_of_middle_tiles += 1

            if tile - 2 in simple_tiles and tile - 1 in simple_tiles:
                count_of_right_tiles += 1

        return (count_of_left_tiles + count_of_middle_tiles + count_of_right_tiles) // 3

    # we know we have no more that 5 tiles of other suit,
    # so this is a simplified version
    @staticmethod
    def _count_of_koutsu(tiles, suit):
        count_of_koutsu = 0

        for x in range(0, 34):
            tile = tiles[x]
            if not tile:
                continue

            if suit(x) and tile >= 3:
                count_of_koutsu += 1

        return count_of_koutsu
