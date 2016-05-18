class Tile(int):
    TILES = '''
        1s 2s 3s 4s 5s 6s 7s 8s 9s
        1p 2p 3p 4p 5p 6p 7p 8p 9p
        1m 2m 3m 4m 5m 6m 7m 8m 9m
        ew sw ww nw
        wd gd rd
    '''.split()

    def as_data(self):
        return self.TILES[self // 4]


class TilesConverter(object):

    @staticmethod
    def to_one_line_string(tiles):
        """
        Convert 136 tiles array to the one line string
        Example of output 123s123p123m33z
        """
        sou = [t for t in tiles if t < 36]

        pin = [t for t in tiles if 36 <= t < 72]
        pin = [t - 36 for t in pin]

        man = [t for t in tiles if 72 <= t < 108]
        man = [t - 72 for t in man]

        honors = [t for t in tiles if t >= 108]
        honors = [t - 108 for t in honors]

        man = man and ''.join([str((i // 4) + 1) for i in man]) + 'm' or ''
        pin = pin and ''.join([str((i // 4) + 1) for i in pin]) + 'p' or ''
        sou = sou and ''.join([str((i // 4) + 1) for i in sou]) + 's' or ''
        honors = honors and ''.join([str((i // 4) + 1) for i in honors]) + 'z' or ''

        return sou + pin + man + honors

    @staticmethod
    def to_34_array(tiles):
        """
        Convert 136 array to the 34 tiles array
        """
        results = [0] * 34
        for tile in tiles:
            tile //= 4
            results[tile] += 1
        return results

    @staticmethod
    def string_to_136_array(sou=None, pin=None, man=None, honors=None):
        """
        Method to convert one line string tiles format to the 136 array
        We need it to increase readability of our tests
        """
        def _split_string(string, offset):
            results = []

            if not string:
                return []

            for i in string:
                tile = offset + (int(i) - 1) * 4
                results.append(tile)

            return results

        results = _split_string(sou, 0)
        results += _split_string(pin, 36)
        results += _split_string(man, 72)
        results += _split_string(honors, 108)

        return results

    @staticmethod
    def find_34_tile_in_136_array(tile34, tiles):
        """
        Our shanten calculator will operate with 34 tiles format,
        after calculations we need to find calculated 34 tile
        in player's 136 tiles.

        For example we had 0 tile from 34 array
        in 136 array it can be present as 0, 1, 2, 3
        """
        if tile34 > 33:
            return None

        tile = tile34 * 4

        possible_tiles = [tile] + [tile + i for i in range(1, 4)]

        found_tile = None
        for possible_tile in possible_tiles:
            if possible_tile in tiles:
                found_tile = possible_tile
                break

        return found_tile
