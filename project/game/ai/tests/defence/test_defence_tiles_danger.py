from game.ai.helpers.defence import TileDanger
from game.table import Table
from utils.test_helpers import find_discard_option, string_to_136_array, string_to_136_tile


def test_tile_danger_and_impossible_wait_fourth_honor():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=string_to_136_array(honors="111"))
    player = table.player

    tiles = string_to_136_array(man="34678", pin="2356", honors="1555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.IMPOSSIBLE_WAIT, honors="1")


def test_tile_danger_and_impossible_wait_latest_tile_behind_kabe():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=string_to_136_array(sou="1112222"))
    player = table.player

    tiles = string_to_136_array(man="34678", pin="2356", honors="1555")
    tile = string_to_136_tile(sou="1")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.IMPOSSIBLE_WAIT, sou="1")


def test_tile_danger_and_honor_third():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=string_to_136_array(honors="11"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="1555")
    tile = string_to_136_tile(sou="8")

    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.HONOR_THIRD, honors="1")


def test_tile_danger_and_non_yakuhai_honor_second():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=string_to_136_array(honors="4"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="4555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.NON_YAKUHAI_HONOR_SECOND, honors="4")


def test_tile_danger_and_non_yakuhai_honor_shonpai():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="4555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.NON_YAKUHAI_HONOR_SHONPAI, honors="4")


def test_tile_danger_and_forms_bonus():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=string_to_136_array(man="9999"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="4555")
    tile = string_to_136_tile(man="6")
    player.init_hand(tiles)
    player.draw_tile(tile)

    discard_options, _ = player.ai.hand_builder.find_discard_options(player.tiles, player.closed_hand, player.melds)
    discard_options = player.ai.defence.check_threat_and_mark_tiles_danger(discard_options)
    discard_option = find_discard_option(discard_options, man="6")
    form_bonus = [
        x
        for x in discard_option.danger.get_danger_reasons(enemy_seat)
        if x["description"] == TileDanger.FORM_BONUS_DESCRIPTION
    ][0]
    assert form_bonus["value"] == 196


def test_tile_danger_and_yakuhai_honor_second():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=string_to_136_array(honors="6"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="5556")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.YAKUHAI_HONOR_SECOND, honors="6")


def test_tile_danger_and_double_yakuhai_honor_second():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=string_to_136_array(honors="2"))
    table.round_wind_number = 5
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.DOUBLE_YAKUHAI_HONOR_SECOND, honors="2")


def test_tile_danger_and_yakuhai_honor_shonpai():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="5556")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.YAKUHAI_HONOR_SHONPAI, honors="6")


def test_tile_danger_and_double_yakuhai_honor_shonpai():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    table.round_wind_number = 5
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.DOUBLE_YAKUHAI_HONOR_SHONPAI, honors="2")


def test_tile_danger_and_terminal_suji_tiles():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), False)
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="9")
    player.init_hand(tiles)
    player.draw_tile(tile)

    # 9 sou is shonpai
    _assert_discard(player, enemy_seat, TileDanger.SUJI_19_SHONPAI, sou="9")

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), False)
    player.discard_tile()
    player.draw_tile(tile)
    # 9 sou is not shonpai anymore
    _assert_discard(player, enemy_seat, TileDanger.SUJI_19_NOT_SHONPAI, sou="9")


def test_tile_danger_and_terminal_kabe_tiles():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=string_to_136_array(sou="2222"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="1")
    player.init_hand(tiles)
    player.draw_tile(tile)

    # 1 sou is shonpai
    _assert_discard(player, enemy_seat, TileDanger.SHONPAI_KABE, sou="1")

    player.discard_tile()
    player.draw_tile(tile)
    # 1 sou is not shonpai anymore
    _assert_discard(player, enemy_seat, TileDanger.NON_SHONPAI_KABE, sou="1")


def test_tile_danger_and_2_8_kabe_tiles():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=string_to_136_array(sou="44446666"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="5")
    player.init_hand(tiles)
    player.draw_tile(tile)

    # 1 sou is shonpai
    _assert_discard(player, enemy_seat, TileDanger.SHONPAI_KABE, sou="5")

    player.discard_tile()
    player.draw_tile(tile)
    # 1 sou is not shonpai anymore
    _assert_discard(player, enemy_seat, TileDanger.NON_SHONPAI_KABE, sou="5")


def _create_table(enemy_seat, discards):
    table = Table()
    for discard in discards:
        table.add_discarded_tile(0, discard, False)
    table.add_called_riichi(enemy_seat)
    return table


def _assert_discard(player, enemy_seat, tile_danger, sou="", pin="", man="", honors=""):
    discard_options, _ = player.ai.hand_builder.find_discard_options(player.tiles, player.closed_hand, player.melds)
    discard_options = player.ai.defence.check_threat_and_mark_tiles_danger(discard_options)
    discard_option = find_discard_option(discard_options, sou=sou, pin=pin, man=man, honors=honors)
    dangers = [
        x
        for x in discard_option.danger.get_danger_reasons(enemy_seat)
        if x["description"] != TileDanger.FORM_BONUS_DESCRIPTION
    ]
    assert dangers == [tile_danger]
