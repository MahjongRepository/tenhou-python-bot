class Meld(object):
    CHI = 'chi'
    PON = 'pon'
    KAN = 'kan'
    CHAKAN = 'chakan'
    NUKI = 'nuki'

    who = None
    tiles = []
    type = None

    def __str__(self):
        return 'Who: {0}, Type: {1}, Tiles: {2}'.format(self.who, self.type, self.tiles)

    # for calls in array
    def __repr__(self):
        return self.__str__()
