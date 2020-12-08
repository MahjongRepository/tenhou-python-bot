from mahjong.tile import TilesConverter
from utils.decisions_logger import MeldPrint


def string_to_136_array(sou="", pin="", man="", honors=""):
    return TilesConverter.string_to_136_array(sou=sou, pin=pin, man=man, honors=honors, has_aka_dora=True)


def string_to_136_tile(sou="", pin="", man="", honors=""):
    return string_to_136_array(
        sou=sou,
        pin=pin,
        man=man,
        honors=honors,
    )[0]


def string_to_34_tile(sou="", pin="", man="", honors=""):
    item = TilesConverter.string_to_136_array(sou=sou, pin=pin, man=man, honors=honors, has_aka_dora=True)
    item[0] //= 4
    return item[0]


def make_meld(meld_type, is_open=True, man="", pin="", sou="", honors="", tiles=None):
    if not tiles:
        tiles = string_to_136_array(man=man, pin=pin, sou=sou, honors=honors)
    meld = MeldPrint(
        meld_type=meld_type,
        tiles=tiles,
        opened=is_open,
        called_tile=tiles[0],
        who=0,
    )
    return meld


def tiles_to_string(tiles_136):
    return TilesConverter.to_one_line_string(tiles_136, print_aka_dora=True)


def find_discard_option(player, sou="", pin="", man="", honors=""):
    discard_options, _ = player.ai.hand_builder.find_discard_options()
    tile = string_to_136_tile(sou=sou, pin=pin, man=man, honors=honors)
    discard_option = [x for x in discard_options if x.tile_to_discard_34 == tile // 4][0]

    player.ai.hand_builder.mark_tiles_riichi_decision(discard_options)

    for x in discard_options:
        if x.shanten in [1]:
            player.ai.hand_builder.calculate_second_level_ukeire(x)

    discard_options, _ = player.ai.defence.mark_tiles_danger_for_threats(discard_options)

    return discard_option


def enemy_called_riichi_helper(table, enemy_seat, riichi_tile=None):
    if not riichi_tile:
        riichi_tile = string_to_136_tile(honors="1")
    table.add_discarded_tile(enemy_seat, riichi_tile, False)
    table.add_called_riichi_step_one(enemy_seat)
    table.add_called_riichi_step_two(enemy_seat)
    table.get_player(enemy_seat).is_ippatsu = False
