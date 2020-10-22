from utils.general import revealed_suits_tiles


class Kabe:
    STRONG_KABE = 0
    WEAK_KABE = 1
    PARTIAL_KABE = 2

    def __init__(self, player):
        self.player = player

    def find_all_kabe(self, tiles_34):
        # all indices shifted to -1
        kabe_matrix = [
            {"indices": [1], "blocked_tiles": [0], "type": Kabe.STRONG_KABE},
            {"indices": [2], "blocked_tiles": [0, 1], "type": Kabe.STRONG_KABE},
            {"indices": [6], "blocked_tiles": [7, 8], "type": Kabe.STRONG_KABE},
            {"indices": [7], "blocked_tiles": [8], "type": Kabe.STRONG_KABE},
            {"indices": [0, 3], "blocked_tiles": [2, 3], "type": Kabe.STRONG_KABE},
            {"indices": [1, 3], "blocked_tiles": [2], "type": Kabe.STRONG_KABE},
            {"indices": [1, 4], "blocked_tiles": [2, 3], "type": Kabe.STRONG_KABE},
            {"indices": [2, 4], "blocked_tiles": [3], "type": Kabe.STRONG_KABE},
            {"indices": [2, 5], "blocked_tiles": [3, 4], "type": Kabe.STRONG_KABE},
            {"indices": [3, 5], "blocked_tiles": [4], "type": Kabe.STRONG_KABE},
            {"indices": [3, 6], "blocked_tiles": [4, 5], "type": Kabe.STRONG_KABE},
            {"indices": [4, 6], "blocked_tiles": [5], "type": Kabe.STRONG_KABE},
            {"indices": [4, 7], "blocked_tiles": [5, 6], "type": Kabe.STRONG_KABE},
            {"indices": [5, 7], "blocked_tiles": [6], "type": Kabe.STRONG_KABE},
            {"indices": [5, 8], "blocked_tiles": [6, 7], "type": Kabe.STRONG_KABE},
            {"indices": [3], "blocked_tiles": [1, 2], "type": Kabe.WEAK_KABE},
            {"indices": [4], "blocked_tiles": [2, 6], "type": Kabe.WEAK_KABE},
            {"indices": [5], "blocked_tiles": [6, 7], "type": Kabe.WEAK_KABE},
            {"indices": [1, 5], "blocked_tiles": [3], "type": Kabe.WEAK_KABE},
            {"indices": [2, 6], "blocked_tiles": [4], "type": Kabe.WEAK_KABE},
            {"indices": [3, 7], "blocked_tiles": [5], "type": Kabe.WEAK_KABE},
        ]

        kabe_tiles_strong = []
        kabe_tiles_weak = []
        kabe_tiles_partial = []

        suits = revealed_suits_tiles(self.player, tiles_34)
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
                if len(list(set(matrix_item["indices"]) - set(kabe_tiles))) == 0:
                    for tile in matrix_item["blocked_tiles"]:
                        if matrix_item["type"] == Kabe.STRONG_KABE:
                            kabe_tiles_strong.append(tile + x * 9)
                        else:
                            kabe_tiles_weak.append(tile + x * 9)

                if len(list(set(matrix_item["indices"]) - set(partial_kabe_tiles))) == 0:
                    for tile in matrix_item["blocked_tiles"]:
                        kabe_tiles_partial.append(tile + x * 9)

        kabe_tiles_unique = []
        kabe_tiles_strong = list(set(kabe_tiles_strong))
        kabe_tiles_weak = list(set(kabe_tiles_weak))
        kabe_tiles_partial = list(set(kabe_tiles_partial))

        for tile in kabe_tiles_strong:
            kabe_tiles_unique.append({"tile": tile, "type": Kabe.STRONG_KABE})

        for tile in kabe_tiles_weak:
            if tile not in kabe_tiles_strong:
                kabe_tiles_unique.append({"tile": tile, "type": Kabe.WEAK_KABE})

        for tile in kabe_tiles_partial:
            if tile not in kabe_tiles_strong and tile not in kabe_tiles_weak:
                kabe_tiles_unique.append({"tile": tile, "type": Kabe.PARTIAL_KABE})

        return kabe_tiles_unique
