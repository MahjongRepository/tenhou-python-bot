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

    # This method will prepare the list of tiles, to use in tenhou shanten analyzer
    # it needed for debug
    @staticmethod
    def prepare_to_tenhou_analyzer(tiles):
        sou = [t for t in tiles if t < 36]

        pin = [t for t in tiles if 36 <= t < 72]
        pin = [t - 36 for t in pin]

        man = [t for t in tiles if 72 <= t < 108]
        man = [t - 72 for t in man]

        honors = [t for t in tiles if t >= 108]
        honors = [t - 108 for t in honors]

        man = ''.join([str((i // 4) + 1) for i in man]) + 'm'
        pin = ''.join([str((i // 4) + 1) for i in pin]) + 'p'
        sou = ''.join([str((i // 4) + 1) for i in sou]) + 's'
        honors = ''.join([str((i // 4) + 1) for i in honors]) + 'z'

        return 'http://tenhou.net/2/?q=' + sou + pin + man + honors
