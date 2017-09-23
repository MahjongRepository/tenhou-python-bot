# -*- coding: utf-8 -*-
from mahjong.utils import is_man, simplify, is_pin, is_sou, plus_dora, is_aka_dora

from game.ai.first_version.defence.defence import Defence, DefenceTile


class Suji(Defence):
    # 1-4-7
    FIRST_SUJI = 1
    # 2-5-8
    SECOND_SUJI = 2
    # 3-6-9
    THIRD_SUJI = 3

    def find_tiles_to_discard(self, players):
        found_suji = []
        for player in players:
            suji = []
            suits = [[], [], []]

            # let's cast each tile to 0-8 presentation
            safe_tiles = player.all_safe_tiles
            for tile in safe_tiles:
                if is_man(tile):
                    suits[0].append(simplify(tile))

                if is_pin(tile):
                    suits[1].append(simplify(tile))

                if is_sou(tile):
                    suits[2].append(simplify(tile))

            for x in range(0, 3):
                simplified_tiles = suits[x]
                base = x * 9

                # 1-4-7
                if 3 in simplified_tiles:
                    suji.append(self.FIRST_SUJI + base)

                # double 1-4-7
                if 0 in simplified_tiles and 6 in simplified_tiles:
                    suji.append(self.FIRST_SUJI + base)

                # 2-5-8
                if 4 in simplified_tiles:
                    suji.append(self.SECOND_SUJI + base)

                # double 2-5-8
                if 1 in simplified_tiles and 7 in simplified_tiles:
                    suji.append(self.SECOND_SUJI + base)

                # 3-6-9
                if 5 in simplified_tiles:
                    suji.append(self.THIRD_SUJI + base)

                # double 3-6-9
                if 2 in simplified_tiles and 8 in simplified_tiles:
                    suji.append(self.THIRD_SUJI + base)

            suji = list(set(suji))

            found_suji.append(suji)

        if not found_suji:
            return []

        common_suji = list(set.intersection(*map(set, found_suji)))

        tiles = []
        for suji in common_suji:
            if not suji:
                continue

            tiles.extend(self._suji_tiles(suji))

        return tiles

    def _suji_tiles(self, suji):
        suji_temp = suji % 9
        base = suji - suji_temp - 1

        first_danger = 20
        second_danger = 30
        third_danger = 40

        result = []
        if suji_temp == self.FIRST_SUJI:
            result = [
                DefenceTile(base + 1, first_danger),
                DefenceTile(base + 4, second_danger),
                DefenceTile(base + 7, third_danger)
            ]

        if suji_temp == self.SECOND_SUJI:
            result = [
                DefenceTile(base + 2, second_danger),
                DefenceTile(base + 5, second_danger),
                DefenceTile(base + 8, second_danger)
            ]

        if suji_temp == self.THIRD_SUJI:
            result = [
                DefenceTile(base + 3, third_danger),
                DefenceTile(base + 6, second_danger),
                DefenceTile(base + 9, first_danger)
            ]

        # mark dora tiles as dangerous tiles to discard
        for tile in result:
            if plus_dora(tile.value * 4, self.table.dora_indicators) or is_aka_dora(tile.value * 4, self.table.has_open_tanyao):
                tile.danger += 100

        return result
