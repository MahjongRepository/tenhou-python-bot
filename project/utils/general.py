import random
import string
from typing import List

from mahjong.constants import EAST
from mahjong.utils import is_honor, is_man, is_pin, is_sou, simplify


# TODO move to mahjong lib
def is_sangenpai(tile_34):
    return tile_34 >= 31


# TODO move to mahjong lib
def is_tiles_same_suit(first_tile_34, second_tile_34):
    if is_pin(first_tile_34) and is_pin(second_tile_34):
        return True
    if is_man(first_tile_34) and is_man(second_tile_34):
        return True
    if is_sou(first_tile_34) and is_sou(second_tile_34):
        return True
    return False


# TODO move to mahjong lib
def is_dora_connector(tile_136: int, dora_indicators_136: List[int]) -> bool:
    tile_34 = tile_136 // 4
    if is_honor(tile_34):
        return False

    for dora_indicator in dora_indicators_136:
        dora_indicator_34 = dora_indicator // 4
        if not is_tiles_same_suit(dora_indicator_34, tile_34):
            continue

        simplified_tile = simplify(tile_34)
        simplified_dora_indicator = simplify(dora_indicator_34)

        if simplified_dora_indicator - 1 == simplified_tile:
            return True

        if simplified_dora_indicator + 1 == simplified_tile:
            return True

    return False


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
