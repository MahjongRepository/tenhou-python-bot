import random
import string

from mahjong.constants import EAST
from mahjong.utils import is_man, is_pin, is_sou, simplify


def make_random_letters_and_digit_string(length=15):
    random_chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(random_chars) for _ in range(length))


def suits_tiles(player, tiles_34):
    """
    Return tiles separated by suits
    """
    suits = [
        [0] * 9,
        [0] * 9,
        [0] * 9,
    ]

    for tile in range(0, EAST):
        total_tiles = player.number_of_revealed_tiles(tile, tiles_34)
        if not total_tiles:
            continue

        suit_index = None
        simplified_tile = simplify(tile)

        if is_man(tile):
            suit_index = 0

        if is_pin(tile):
            suit_index = 1

        if is_sou(tile):
            suit_index = 2

        suits[suit_index][simplified_tile] += total_tiles

    return suits
