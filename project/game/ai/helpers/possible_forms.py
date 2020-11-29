from game.ai.helpers.defence import TileDanger
from mahjong.constants import EAST
from mahjong.tile import TilesConverter
from utils.general import revealed_suits_tiles


class PossibleFormsAnalyzer:
    POSSIBLE_TANKI = 1
    POSSIBLE_SYANPON = 2
    POSSIBLE_PENCHAN = 3
    POSSIBLE_KANCHAN = 4
    POSSIBLE_RYANMEN = 5
    POSSIBLE_RYANMEN_SIDES = 6

    def __init__(self, player):
        self.player = player

    def calculate_possible_forms(self, safe_tiles):
        possible_forms_34 = [None] * 34

        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)

        # first of all let's find suji for suits tiles
        suits = revealed_suits_tiles(self.player, closed_hand_34)
        for x in range(0, 3):
            suit = suits[x]

            for y in range(0, 9):
                tile_34_index = y + x * 9

                # we are only interested in tiles that we can discard
                if closed_hand_34[tile_34_index] == 0:
                    continue

                forms_count = self._init_zero_forms_count()
                possible_forms_34[tile_34_index] = forms_count

                # that means there are no possible forms for him to wait (we don't consider furiten here,
                # because we are defending from enemy taking ron)
                if tile_34_index in safe_tiles:
                    continue

                # tanki
                forms_count[self.POSSIBLE_TANKI] = 4 - suit[y]

                # syanpon
                if suit[y] == 1:
                    forms_count[self.POSSIBLE_SYANPON] = 3
                if suit[y] == 2:
                    forms_count[self.POSSIBLE_SYANPON] = 1
                else:
                    forms_count[self.POSSIBLE_SYANPON] = 0

                # penchan
                if y == 2:
                    forms_count[self.POSSIBLE_PENCHAN] = (4 - suit[0]) * (4 - suit[1])
                elif y == 6:
                    forms_count[self.POSSIBLE_PENCHAN] = (4 - suit[8]) * (4 - suit[7])

                # kanchan
                if 1 <= y <= 7:
                    tiles_cnt_left = 4 - suit[y - 1]
                    tiles_cnt_right = 4 - suit[y + 1]
                    forms_count[self.POSSIBLE_KANCHAN] = tiles_cnt_left * tiles_cnt_right

                # ryanmen
                if 0 <= y <= 2:
                    if not (tile_34_index + 3) in safe_tiles:
                        forms_right = (4 - suit[y + 1]) * (4 - suit[y + 2])
                        if forms_right != 0:
                            forms_count[self.POSSIBLE_RYANMEN_SIDES] = 1
                            forms_count[self.POSSIBLE_RYANMEN] = (4 - suit[y + 1]) * (4 - suit[y + 2])
                elif 3 <= y <= 5:
                    if not (tile_34_index - 3) in safe_tiles:
                        forms_left = (4 - suit[y - 1]) * (4 - suit[y - 2])
                        if forms_left != 0:
                            forms_count[self.POSSIBLE_RYANMEN_SIDES] += 1
                            forms_count[self.POSSIBLE_RYANMEN] += forms_left
                    if not (tile_34_index + 3) in safe_tiles:
                        forms_right = (4 - suit[y + 1]) * (4 - suit[y + 2])
                        if forms_right != 0:
                            forms_count[self.POSSIBLE_RYANMEN_SIDES] += 1
                            forms_count[self.POSSIBLE_RYANMEN] += forms_right
                else:
                    if not (tile_34_index - 3) in safe_tiles:
                        forms_left = (4 - suit[y - 1]) * (4 - suit[y - 2])
                        if forms_left != 0:
                            forms_count[self.POSSIBLE_RYANMEN] = (4 - suit[y - 1]) * (4 - suit[y - 2])
                            forms_count[self.POSSIBLE_RYANMEN_SIDES] = 1

        for tile_34_index in range(EAST, 34):
            if closed_hand_34[tile_34_index] == 0:
                continue

            forms_count = self._init_zero_forms_count()
            possible_forms_34[tile_34_index] = forms_count

            total_tiles = self.player.number_of_revealed_tiles(tile_34_index, closed_hand_34)

            # tanki
            forms_count[self.POSSIBLE_TANKI] = 4 - total_tiles

            # syanpon
            forms_count[self.POSSIBLE_SYANPON] = 3 - total_tiles if total_tiles < 3 else 0

        return possible_forms_34

    @staticmethod
    def calculate_possible_forms_total(forms_count):
        total = 0
        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_TANKI]
        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_SYANPON]
        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_PENCHAN]
        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_KANCHAN]
        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_RYANMEN]
        return total

    @staticmethod
    def calculate_possible_forms_danger(forms_count):
        danger = 0
        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_TANKI] * TileDanger.FORM_BONUS_TANKI
        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_SYANPON] * TileDanger.FORM_BONUS_SYANPON
        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_PENCHAN] * TileDanger.FORM_BONUS_PENCHAN
        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_KANCHAN] * TileDanger.FORM_BONUS_KANCHAN
        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_RYANMEN] * TileDanger.FORM_BONUS_RYANMEN
        return danger

    def _init_zero_forms_count(self):
        forms_count = dict()
        forms_count[self.POSSIBLE_TANKI] = 0
        forms_count[self.POSSIBLE_SYANPON] = 0
        forms_count[self.POSSIBLE_PENCHAN] = 0
        forms_count[self.POSSIBLE_KANCHAN] = 0
        forms_count[self.POSSIBLE_RYANMEN] = 0
        forms_count[self.POSSIBLE_RYANMEN_SIDES] = 0
        return forms_count
