from mahjong.hand import HandDivider
from mahjong.tile import TilesConverter


class TestMixin(object):

    def _string_to_open_34_set(self, sou='', pin='', man='', honors=''):
        open_set = TilesConverter.string_to_136_array(sou=sou, pin=pin, man=man, honors=honors)
        open_set[0] //= 4
        open_set[1] //= 4
        open_set[2] //= 4
        return open_set

    def _string_to_34_tile(self, sou='', pin='', man='', honors=''):
        item = TilesConverter.string_to_136_array(sou=sou, pin=pin, man=man, honors=honors)
        item[0] //= 4
        return item[0]

    def _string_to_34_array(self, sou='', pin='', man='', honors=''):
        return TilesConverter.string_to_34_array(sou=sou, pin=pin, man=man, honors=honors)

    def _string_to_136_array(self, sou='', pin='', man='', honors=''):
        return TilesConverter.string_to_136_array(sou=sou, pin=pin, man=man, honors=honors)

    def _string_to_136_tile(self, sou='', pin='', man='', honors=''):
        return TilesConverter.string_to_136_array(sou=sou, pin=pin, man=man, honors=honors)[0]

    def _to_34_array(self, tiles):
        return TilesConverter.to_34_array(tiles)

    def _hand(self, tiles, hand_index=0):
        hand_divider = HandDivider()
        return hand_divider.divide_hand(tiles, [], [])[hand_index]
