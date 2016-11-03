# -*- coding: utf-8 -*-
from mahjong.tile import TilesConverter


class Meld(object):
    CHI = 'chi'
    PON = 'pon'
    KAN = 'kan'
    CHAKAN = 'chakan'
    NUKI = 'nuki'

    who = None
    tiles = []
    type = None
    from_who = None

    def __str__(self):
        return 'Type: {}, Tiles: {} {}'.format(self.type, TilesConverter.to_one_line_string(self.tiles), self.tiles)

    # for calls in array
    def __repr__(self):
        return self.__str__()
