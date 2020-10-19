from mahjong.meld import Meld
from mahjong.tile import TilesConverter


def string_to_136_array(sou="", pin="", man="", honors=""):
    return TilesConverter.string_to_136_array(
        sou=sou,
        pin=pin,
        man=man,
        honors=honors,
    )


def string_to_136_tile(sou="", pin="", man="", honors=""):
    return string_to_136_array(
        sou=sou,
        pin=pin,
        man=man,
        honors=honors,
    )[0]


def string_to_34_tile(sou="", pin="", man="", honors=""):
    item = TilesConverter.string_to_136_array(
        sou=sou,
        pin=pin,
        man=man,
        honors=honors,
    )
    item[0] //= 4
    return item[0]


def make_meld(meld_type, is_open=True, man="", pin="", sou="", honors=""):
    tiles = string_to_136_array(man=man, pin=pin, sou=sou, honors=honors)
    meld = Meld(
        meld_type=meld_type,
        tiles=tiles,
        opened=is_open,
        called_tile=tiles[0],
        who=0,
    )
    return meld


def tiles_to_string(tiles_136):
    return TilesConverter.to_one_line_string(tiles_136)


def find_discard_option(player, sou="", pin="", man="", honors=""):
    discard_options, _ = player.ai.hand_builder.find_discard_options(player.tiles, player.closed_hand, player.melds)
    tile = string_to_136_tile(sou=sou, pin=pin, man=man, honors=honors)
    discard_option = [x for x in discard_options if x.tile_to_discard == tile // 4][0]

    for x in discard_options:
        if x.shanten in [1]:
            player.ai.hand_builder.calculate_second_level_ukeire(x, player.tiles, player.melds)

    discard_options, _ = player.ai.defence.mark_tiles_danger_for_threats(discard_options)

    return discard_option
