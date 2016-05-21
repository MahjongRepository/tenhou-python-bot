# -*- coding: utf-8 -*-
import math


class Shanten(object):
    AGARI_STATE = -1

    tiles = []
    number_melds = 0
    number_tatsu = 0
    number_pairs = 0
    number_jidahai = 0
    number_characters = 0
    number_isolated_tiles = 0
    min_shanten = 0

    def init(self, tiles):
        self.tiles = tiles
        self.number_melds = 0
        self.number_tatsu = 0
        self.number_pairs = 0
        self.number_jidahai = 0
        self.number_characters = 0
        self.number_isolated_tiles = 0
        self.min_shanten = 8

    def update_result(self):
        ret_shanten = 8 - self.number_melds * 2 - self.number_tatsu - self.number_pairs
        n_mentsu_kouho = self.number_melds + self.number_tatsu
        if self.number_pairs:
            n_mentsu_kouho += self.number_pairs - 1
        elif self.number_characters and self.number_isolated_tiles:
            if (self.number_characters | self.number_isolated_tiles) == self.number_characters:
                ret_shanten += 1

        if n_mentsu_kouho > 4:
            ret_shanten += n_mentsu_kouho - 4

        if ret_shanten != Shanten.AGARI_STATE and ret_shanten < self.number_jidahai:
            ret_shanten = self.number_jidahai

        if ret_shanten < self.min_shanten:
            self.min_shanten = ret_shanten

    def increase_set(self, k):
        self.tiles[k] -= 3
        self.number_melds += 1

    def decrease_set(self, k):
        self.tiles[k] += 3
        self.number_melds -= 1

    def increase_pair(self, k):
        self.tiles[k] -= 2
        self.number_pairs += 1

    def decrease_pair(self, k):
        self.tiles[k] += 2
        self.number_pairs -= 1

    def increase_syuntsu(self, k):
        self.tiles[k] -= 1
        self.tiles[k + 1] -= 1
        self.tiles[k + 2] -= 1
        self.number_melds += 1

    def decrease_syuntsu(self, k):
        self.tiles[k] += 1
        self.tiles[k + 1] += 1
        self.tiles[k + 2] += 1
        self.number_melds -= 1

    def increase_tatsu_first(self, k):
        self.tiles[k] -= 1
        self.tiles[k + 1] -= 1
        self.number_tatsu += 1

    def decrease_tatsu_first(self, k):
        self.tiles[k] += 1
        self.tiles[k + 1] += 1
        self.number_tatsu -= 1

    def increase_tatsu_second(self, k):
        self.tiles[k] -= 1
        self.tiles[k + 2] -= 1
        self.number_tatsu += 1

    def decrease_tatsu_second(self, k):
        self.tiles[k] += 1
        self.tiles[k + 2] += 1
        self.number_tatsu -= 1

    def increase_isolated_tile(self, k):
        self.tiles[k] -= 1
        self.number_isolated_tiles |= (1 << k)

    def decrease_isolated_tile(self, k):
        self.tiles[k] += 1
        self.number_isolated_tiles |= (1 << k)

    def scan_chitoitsu_and_kokushi(self):
        shanten = self.min_shanten

        indices = [0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33]

        completed_terminals = 0
        for i in indices:
            completed_terminals += self.tiles[i] >= 2

        terminals = 0
        for i in indices:
            terminals += self.tiles[i] != 0

        indices = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25]

        completed_pairs = completed_terminals
        for i in indices:
            completed_pairs += self.tiles[i] >= 2

        pairs = terminals
        for i in indices:
            pairs += self.tiles[i] != 0

        ret_shanten = 6 - completed_pairs + (pairs < 7 and 7 - pairs or 0)
        if ret_shanten < shanten:
            shanten = ret_shanten

        ret_shanten = 13 - terminals - (completed_terminals and 1 or 0)
        if ret_shanten < shanten:
            shanten = ret_shanten

        return shanten

    def remove_character_tiles(self, nc):
        number = 0
        isolated = 0

        for i in range(27, 34):
            if self.tiles[i] == 4:
                self.number_melds += 1
                self.number_jidahai += 1
                number |= (1 << (i - 27))
                isolated |= (1 << (i - 27))

            if self.tiles[i] == 3:
                self.number_melds += 1

            if self.tiles[i] == 2:
                self.number_pairs += 1

            if self.tiles[i] == 1:
                isolated |= (1 << (i - 27))

        if self.number_jidahai and (nc % 3) == 2:
            self.number_jidahai -= 1

        if isolated:
            self.number_isolated_tiles |= (1 << 27)
            if (number | isolated) == number:
                self.number_characters |= (1 << 27)

    def scan(self, init_mentsu):
        self.number_characters = 0
        for i in range(0, 27):
            self.number_characters |= (self.tiles[i] == 4) << i
        self.number_melds += init_mentsu
        self.run(0)

    def run(self, depth):

        if self.min_shanten == Shanten.AGARI_STATE:
            return

        while not self.tiles[depth]:
            depth += 1

            if depth >= 27:
                break

        if depth >= 27:
            return self.update_result()

        i = depth
        if i > 8:
            i -= 9
        if i > 8:
            i -= 9

        if self.tiles[depth] == 4:
            self.increase_set(depth)
            if i < 7 and self.tiles[depth + 2]:
                if self.tiles[depth + 1]:
                    self.increase_syuntsu(depth)
                    self.run(depth + 1)
                    self.decrease_syuntsu(depth)
                self.increase_tatsu_second(depth)
                self.run(depth + 1)
                self.decrease_tatsu_second(depth)

            if i < 8 and self.tiles[depth + 1]:
                self.increase_tatsu_first(depth)
                self.run(depth + 1)
                self.decrease_tatsu_first(depth)

            self.increase_isolated_tile(depth)
            self.run(depth + 1)
            self.decrease_isolated_tile(depth)
            self.decrease_set(depth)
            self.increase_pair(depth)

            if i < 7 and self.tiles[depth + 2]:
                if self.tiles[depth + 1]:
                    self.increase_syuntsu(depth)
                    self.run(depth)
                    self.decrease_syuntsu(depth)
                self.increase_tatsu_second(depth)
                self.run(depth + 1)
                self.decrease_tatsu_second(depth)

            if i < 8 and self.tiles[depth + 1]:
                self.increase_tatsu_first(depth)
                self.run(depth + 1)
                self.decrease_tatsu_first(depth)

            self.decrease_pair(depth)

        if self.tiles[depth] == 3:
            self.increase_set(depth)
            self.run(depth + 1)
            self.decrease_set(depth)
            self.increase_pair(depth)

            if i < 7 and self.tiles[depth + 1] and self.tiles[depth + 2]:
                self.increase_syuntsu(depth)
                self.run(depth + 1)
                self.decrease_syuntsu(depth)
            else:
                if i < 7 and self.tiles[depth + 2]:
                    self.increase_tatsu_second(depth)
                    self.run(depth + 1)
                    self.decrease_tatsu_second(depth)

                if i < 8 and self.tiles[depth + 1]:
                    self.increase_tatsu_first(depth)
                    self.run(depth + 1)
                    self.decrease_tatsu_first(depth)

            self.decrease_pair(depth)

            if i < 7 and self.tiles[depth + 2] >= 2 and self.tiles[depth + 1] >= 2:
                self.increase_syuntsu(depth)
                self.increase_syuntsu(depth)
                self.run(depth)
                self.decrease_syuntsu(depth)
                self.decrease_syuntsu(depth)

        if self.tiles[depth] == 2:
            self.increase_pair(depth)
            self.run(depth + 1)
            self.decrease_pair(depth)
            if i < 7 and self.tiles[depth + 2] and self.tiles[depth + 1]:
                self.increase_syuntsu(depth)
                self.run(depth)
                self.decrease_syuntsu(depth)

        if self.tiles[depth] == 1:
            if i < 6 and self.tiles[depth + 1] == 1 and self.tiles[depth + 2] and self.tiles[depth + 3] != 4:
                self.increase_syuntsu(depth)
                self.run(depth + 2)
                self.decrease_syuntsu(depth)
            else:
                self.increase_isolated_tile(depth)
                self.run(depth + 1)
                self.decrease_isolated_tile(depth)

                if i < 7 and self.tiles[depth + 2]:
                    if self.tiles[depth + 1]:
                        self.increase_syuntsu(depth)
                        self.run(depth + 1)
                        self.decrease_syuntsu(depth)
                    self.increase_tatsu_second(depth)
                    self.run(depth + 1)
                    self.decrease_tatsu_second(depth)

                if i < 8 and self.tiles[depth + 1]:
                    self.increase_tatsu_first(depth)
                    self.run(depth + 1)
                    self.decrease_tatsu_first(depth)

    def calculate_shanten(self, tiles):
        self.init(tiles)

        count_of_tiles = sum(self.tiles)

        if count_of_tiles > 14:
            return -2

        self.min_shanten = self.scan_chitoitsu_and_kokushi()
        self.remove_character_tiles(count_of_tiles)

        init_mentsu = math.floor((14 - count_of_tiles) / 3)
        self.scan(init_mentsu)

        return self.min_shanten
