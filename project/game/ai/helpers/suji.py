from mahjong.utils import is_man, is_pin, is_sou, simplify


class Suji:
    # 1-4-7
    FIRST_SUJI = 1
    # 2-5-8
    SECOND_SUJI = 2
    # 3-6-9
    THIRD_SUJI = 3

    def __init__(self, player):
        self.player = player

    def find_suji(self, tiles_136):
        tiles_34 = list(set([x // 4 for x in tiles_136]))

        suji = []
        suits = [[], [], []]

        # let's cast each tile to 0-8 presentation
        for tile in tiles_34:
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

        all_suji = list(set(suji))
        result = []
        for suji in all_suji:
            suji_temp = suji % 9
            base = suji - suji_temp - 1

            if suji_temp == self.FIRST_SUJI:
                result += [base + 1, base + 4, base + 7]

            if suji_temp == self.SECOND_SUJI:
                result += [base + 2, base + 5, base + 8]

            if suji_temp == self.THIRD_SUJI:
                result += [base + 3, base + 6, base + 9]

        return result
