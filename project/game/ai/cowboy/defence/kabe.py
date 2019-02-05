# -*- coding: utf-8 -*-
from mahjong.constants import EAST
from mahjong.utils import simplify, is_man, is_pin, is_sou

from game.ai.first_version.defence.defence import Defence, DefenceTile


class Kabe(Defence):

    def find_tiles_to_discard(self, _):
        results = []

        # all indices shifted to -1
        kabe_matrix = [
            {'indices': [1], 'blocked_tiles': [0]},
            {'indices': [2], 'blocked_tiles': [0, 1]},
            {'indices': [3], 'blocked_tiles': [1, 2]},
            {'indices': [4], 'blocked_tiles': [2, 6]},
            {'indices': [5], 'blocked_tiles': [6, 7]},
            {'indices': [6], 'blocked_tiles': [7, 8]},
            {'indices': [7], 'blocked_tiles': [8]},
            {'indices': [1, 5], 'blocked_tiles': [3]},
            {'indices': [2, 6], 'blocked_tiles': [4]},
            {'indices': [3, 7], 'blocked_tiles': [5]},
            {'indices': [1, 4], 'blocked_tiles': [2, 3]},
            {'indices': [2, 5], 'blocked_tiles': [3, 4]},
            {'indices': [3, 6], 'blocked_tiles': [4, 5]},
            {'indices': [4, 7], 'blocked_tiles': [5, 6]},
        ]

        suits = self._suits_tiles(self.defence.hand_34)
        for x in range(0, 3):
            suit = suits[x]
            # "kabe" - 4 revealed tiles
            kabe_tiles = []
            for y in range(0, 9):
                suit_tile = suit[y]
                if suit_tile == 4:
                    kabe_tiles.append(y)

            blocked_indices = []
            for matrix_item in kabe_matrix:
                all_indices = len(list(set(matrix_item['indices']) - set(kabe_tiles))) == 0
                if all_indices:
                    blocked_indices.extend(matrix_item['blocked_tiles'])

            blocked_indices = list(set(blocked_indices))
            for index in blocked_indices:
                # let's find 34 tile index
                tile = index + x * 9
                if self.player.total_tiles(tile, self.defence.hand_34) == 4:
                    results.append(DefenceTile(tile, DefenceTile.SAFE))

                if self.player.total_tiles(tile, self.defence.hand_34) == 3:
                    results.append(DefenceTile(tile, DefenceTile.ALMOST_SAFE_TILE))

        return results

    def _suits_tiles(self, tiles_34):
        """
        Return tiles separated by suits
        :param tiles_34:
        :return:
        """
        suits = [
            [0] * 9,
            [0] * 9,
            [0] * 9,
        ]

        for tile in range(0, EAST):
            total_tiles = self.player.total_tiles(tile, tiles_34)
            if not total_tiles:
                continue

            suit_index = None
            simplified_tile = simplify(tile)

            if is_man(tile):
                suit_index = 0

            if is_pin(tile):
                suit_index = 1

            if is_sou(tile):
                suit_index = 2

            suits[suit_index][simplified_tile] += total_tiles

        return suits
