from copy import copy

import pytest
from game.ai.helpers.defence import TileDanger
from game.table import Table
from mahjong.constants import FIVE_RED_SOU
from utils.decisions_logger import MeldPrint
from utils.test_helpers import find_discard_option, make_meld, string_to_136_array, string_to_136_tile


def test_tile_danger_genbutsu():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), False)
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="6")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, sou="6")


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

    discard_option = find_discard_option(player, man="6")
    form_bonus = [
        x
        for x in discard_option.danger.get_danger_reasons(enemy_seat)
        if x["description"] == TileDanger.FORM_BONUS_DESCRIPTION
    ][0]
    assert form_bonus["value"] == 308


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
    player.discard_tile(string_to_136_tile(honors="5"))
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


def test_tile_danger_and_2_8_suji_tiles():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    player = table.player

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="2"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="3"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="7"), False)

    tiles = string_to_136_array(sou="2378", pin="4", man="56", honors="233555")
    tile = string_to_136_tile(honors="3")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SUJI, sou="2")
    _assert_discard(player, enemy_seat, TileDanger.SUJI, sou="3")
    _assert_discard(player, enemy_seat, TileDanger.SUJI, sou="7")
    _assert_discard(player, enemy_seat, TileDanger.SUJI, sou="8")
    _assert_discard(player, enemy_seat, TileDanger.SUJI, pin="4")
    _assert_discard(player, enemy_seat, TileDanger.SUJI, man="5")
    _assert_discard(player, enemy_seat, TileDanger.SUJI, man="6")


def test_tile_danger_and_ryanmen_wait():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="5")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.RYANMEN_BASE_DOUBLE, sou="5")
    player.discard_tile()

    tile = string_to_136_tile(sou="9")
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.RYANMEN_BASE_SINGLE, sou="9")
    player.discard_tile()

    # if there is a kabe on one side, double-ryanmen becomes a single-ryanmen
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="7"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="7"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="7"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="7"), False)

    tile = string_to_136_tile(sou="5")
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.RYANMEN_BASE_SINGLE, sou="5")


def test_tile_danger_and_dora():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    table.add_dora_indicator(string_to_136_tile(sou="2"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="3")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.DORA_BONUS, sou="3")

    table.add_dora_indicator(string_to_136_tile(sou="2"))
    updated = copy(TileDanger.DORA_BONUS)
    updated["value"] = 2 * TileDanger.DORA_BONUS["value"]
    _assert_discard(player, enemy_seat, updated, sou="3")


def test_tile_danger_and_aka_dora():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = FIVE_RED_SOU
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.DORA_BONUS, sou="5")


@pytest.mark.skip("Skipped until danger values tuning is finished")
def test_tile_total_danger():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[])
    table.add_dora_indicator(string_to_136_tile(sou="3"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="4")
    player.init_hand(tiles)
    player.draw_tile(tile)

    discard_option = find_discard_option(player, sou="4")

    assert discard_option.danger.get_total_danger_for_player(enemy_seat) == 388


def test_tile_danger_against_tanyao_threat():
    table = Table()
    player = table.player

    enemy_seat = 2
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, pin="234"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, sou="333"))
    table.player.round_step = 2
    table.add_dora_indicator(string_to_136_tile(pin="1"))
    table.add_dora_indicator(string_to_136_tile(pin="2"))

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat

    tiles = string_to_136_array(man="11134", pin="1569", honors="2555")
    tile = string_to_136_tile(sou="4")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, man="1")
    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, pin="9")
    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, honors="2")
    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, pin="5", positive=False)


def test_tile_danger_against_honitsu_threat():
    table = Table()
    table.add_dora_indicator(string_to_136_tile(pin="1"))
    player = table.player

    enemy_seat = 1
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, pin="567"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, pin="123"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, pin="345"))
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="2"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="2"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), False)

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat

    tiles = string_to_136_array(man="11134", pin="1569", honors="2555")
    tile = string_to_136_tile(sou="4")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, man="3")
    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, sou="4")
    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, pin="5", positive=False)


def _create_table(enemy_seat, discards):
    table = Table()
    table.has_aka_dora = True
    for discard in discards:
        table.add_discarded_tile(0, discard, False)
    table.add_called_riichi(enemy_seat)
    return table


def _assert_discard(player, enemy_seat, tile_danger, positive=True, sou="", pin="", man="", honors=""):
    discard_option = find_discard_option(player, sou=sou, pin=pin, man=man, honors=honors)

    danger = [
        x
        for x in discard_option.danger.get_danger_reasons(enemy_seat)
        if x["description"] == tile_danger["description"]
    ]
    if positive:
        assert len(danger) > 0
        assert danger[0]["value"] == tile_danger["value"]
        assert danger[0]["description"] == tile_danger["description"]
    else:
        assert len(danger) == 0
