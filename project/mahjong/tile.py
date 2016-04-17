class Tile(int):
    TILES = '''
        1s 2s 3s 4s 5s 6s 7s 8s 9s
        1p 2p 3p 4p 5p 6p 7p 8p 9p
        1m 2m 3m 4m 5m 6m 7m 8m 9m
        ew sw ww nw
        wd gd rd
    '''.split()

    def __str__(self):
        return self.as_data()

    def __repr__(self):
        return self.__str__()

    def as_data(self):
        return self.TILES[self // 4]