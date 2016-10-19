from mahjong.constants import EAST


def is_dora(tile, dora_indicators):
    """
    :param tile: int 136 tiles format
    :param dora_indicators: array of 136 tiles format
    :return: boolean
    """
    tile_index = tile // 4

    for dora in dora_indicators:
        dora //= 4

        # sou, pin, man
        if tile_index < EAST:

            # with indicator 9, dora will be 1
            if dora == 8:
                dora = -1
            elif dora == 17:
                dora = 8
            elif dora == 26:
                dora = 17

            if tile_index == dora + 1:
                return True
        else:
            dora -= 9 * 3
            tile_index -= 9 * 3

            # dora indicator is north
            if dora == 3:
                dora = -1

            # dora indicator is hatsu
            if dora == 6:
                dora = 3

            if tile_index == dora + 1:
                return True

    return False


def is_chi(item):
    """
    :param item: array of tile 34 indices
    :return: boolean
    """
    if len(item) != 3:
        return False

    return item[0] == item[1] - 1 == item[2] - 2


def is_pon(item):
    """
    :param item: array of tile 34 indices
    :return: boolean
    """
    if len(item) != 3:
        return False

    return item[0] == item[1] == item[2]


def is_pair(item):
    """
    :param item: array of tile 34 indices
    :return: boolean
    """
    return len(item) == 2


def is_sou(tile):
    """
    :param tile: 34 tile format
    :return: boolean
    """
    return tile <= 8


def is_pin(tile):
    """
    :param tile: 34 tile format
    :return: boolean
    """
    return 8 < tile <= 17


def is_man(tile):
    """
    :param tile: 34 tile format
    :return: boolean
    """
    return 17 < tile <= 26
