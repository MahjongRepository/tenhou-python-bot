import random
import string

from mahjong.constants import EAST
from mahjong.utils import is_man, is_pin, is_sou, simplify


def is_sangenpai(tile_34):
    return tile_34 >= 31


def make_random_letters_and_digit_string(length=15):
    random_chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(random_chars) for _ in range(length))


def revealed_suits_tiles(player, tiles_34):
    """
    Return all reviled tiles separated by suits for provided tiles list
    """
    return _suits_tiles_helper(
        tiles_34, lambda _tile_34_index, _tiles_34: player.number_of_revealed_tiles(_tile_34_index, _tiles_34)
    )


def separate_tiles_by_suits(tiles_34):
    """
    Return tiles separated by suits for provided tiles list
    """
    return _suits_tiles_helper(tiles_34, lambda _tile_34_index, _tiles_34: _tiles_34[_tile_34_index])


def _suits_tiles_helper(tiles_34, total_tiles_lambda):
    """
    Separate tiles by suit
    """
    suits = [
        [0] * 9,
        [0] * 9,
        [0] * 9,
    ]

    for tile_34_index in range(0, EAST):
        total_tiles = total_tiles_lambda(tile_34_index, tiles_34)
        if not total_tiles:
            continue

        suit_index = None
        simplified_tile = simplify(tile_34_index)

        if is_man(tile_34_index):
            suit_index = 0

        if is_pin(tile_34_index):
            suit_index = 1

        if is_sou(tile_34_index):
            suit_index = 2

        suits[suit_index][simplified_tile] += total_tiles

    return suits
