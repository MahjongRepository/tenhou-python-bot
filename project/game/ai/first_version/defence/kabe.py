# -*- coding: utf-8 -*-
from mahjong.constants import EAST
from mahjong.utils import simplify, is_man, is_pin, is_sou

from game.ai.first_version.defence.defence import Defence, DefenceTile


class Kabe(Defence):

    def find_all_kabe(self, tiles_34):
        # all indices shifted to -1
        kabe_matrix = [
            {'indices': [1], 'blocked_tiles': [0], 'type': KabeTile.STRONG_KABE},
            {'indices': [2], 'blocked_tiles': [0, 1], 'type': KabeTile.STRONG_KABE},
            {'indices': [6], 'blocked_tiles': [7, 8], 'type': KabeTile.STRONG_KABE},
            {'indices': [7], 'blocked_tiles': [8], 'type': KabeTile.STRONG_KABE},
            {'indices': [0, 3], 'blocked_tiles': [2, 3], 'type': KabeTile.STRONG_KABE},
            {'indices': [1, 3], 'blocked_tiles': [2], 'type': KabeTile.STRONG_KABE},
            {'indices': [1, 4], 'blocked_tiles': [2, 3], 'type': KabeTile.STRONG_KABE},
            {'indices': [2, 4], 'blocked_tiles': [3], 'type': KabeTile.STRONG_KABE},
            {'indices': [2, 5], 'blocked_tiles': [3, 4], 'type': KabeTile.STRONG_KABE},
            {'indices': [3, 5], 'blocked_tiles': [4], 'type': KabeTile.STRONG_KABE},
            {'indices': [3, 6], 'blocked_tiles': [4, 5], 'type': KabeTile.STRONG_KABE},
            {'indices': [4, 6], 'blocked_tiles': [5], 'type': KabeTile.STRONG_KABE},
            {'indices': [4, 7], 'blocked_tiles': [5, 6], 'type': KabeTile.STRONG_KABE},
            {'indices': [5, 7], 'blocked_tiles': [6], 'type': KabeTile.STRONG_KABE},
            {'indices': [5, 8], 'blocked_tiles': [6, 7], 'type': KabeTile.STRONG_KABE},

            {'indices': [3], 'blocked_tiles': [1, 2], 'type': KabeTile.WEAK_KABE},
            {'indices': [4], 'blocked_tiles': [2, 6], 'type': KabeTile.WEAK_KABE},
            {'indices': [5], 'blocked_tiles': [6, 7], 'type': KabeTile.WEAK_KABE},
            {'indices': [1, 5], 'blocked_tiles': [3], 'type': KabeTile.WEAK_KABE},
            {'indices': [2, 6], 'blocked_tiles': [4], 'type': KabeTile.WEAK_KABE},
            {'indices': [3, 7], 'blocked_tiles': [5], 'type': KabeTile.WEAK_KABE},
        ]

        kabe_tiles_strong = []
        kabe_tiles_weak = []
        kabe_tiles_partial = []

        suits = self._suits_tiles(tiles_34)
        for x in range(0, 3):
            suit = suits[x]
            # "kabe" - 4 revealed tiles
            kabe_tiles = []
            partial_kabe_tiles = []
            for y in range(0, 9):
                suit_tile = suit[y]
                if suit_tile == 4:
                    kabe_tiles.append(y)
                elif suit_tile == 3:
                    partial_kabe_tiles.append(y)

            for matrix_item in kabe_matrix:
                if len(list(set(matrix_item['indices']) - set(kabe_tiles))) == 0:
                    for tile in matrix_item['blocked_tiles']:
                        if matrix_item['type'] == KabeTile.STRONG_KABE:
                            kabe_tiles_strong.append(tile + x * 9)
                        else:
                            kabe_tiles_weak.append(tile + x * 9)

                if len(list(set(matrix_item['indices']) - set(partial_kabe_tiles))) == 0:
                    for tile in matrix_item['blocked_tiles']:
                        kabe_tiles_partial.append(tile + x * 9)

        kabe_tiles_unique = []
        kabe_tiles_strong = list(set(kabe_tiles_strong))
        kabe_tiles_weak = list(set(kabe_tiles_weak))
        kabe_tiles_partial = list(set(kabe_tiles_partial))

        for tile in kabe_tiles_strong:
            kabe_tiles_unique.append(KabeTile(tile, KabeTile.STRONG_KABE))

        for tile in kabe_tiles_weak:
            if tile not in kabe_tiles_strong:
                kabe_tiles_unique.append(KabeTile(tile, KabeTile.WEAK_KABE))

        for tile in kabe_tiles_partial:
            if tile not in kabe_tiles_strong and tile not in kabe_tiles_weak:
                kabe_tiles_unique.append(KabeTile(tile, KabeTile.PARTIAL_KABE))

        return kabe_tiles_unique

    def find_tiles_to_discard(self, _):
        all_kabe = self.find_all_kabe(self.defence.closed_hand_34)

        results = []

        for kabe in all_kabe:
            # we don't use it for defence now
            if kabe.kabe_type == KabeTile.PARTIAL_KABE:
                continue

            tile = kabe.tile_34
            if self.player.total_tiles(tile, self.defence.closed_hand_34) == 4:
                results.append(DefenceTile(tile, DefenceTile.SAFE))

            if self.player.total_tiles(tile, self.defence.closed_hand_34) == 3:
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


class KabeTile(object):
    STRONG_KABE = 0
    WEAK_KABE = 1
    PARTIAL_KABE = 2

    tile_34 = None
    kabe_type = None

    def __init__(self, tile_34, kabe_type):
        self.tile_34 = tile_34
        self.kabe_type = kabe_type
