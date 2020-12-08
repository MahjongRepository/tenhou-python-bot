from copy import copy

import pytest
from game.ai.helpers.defence import TileDanger
from game.table import Table
from mahjong.constants import FIVE_RED_SOU
from utils.decisions_logger import MeldPrint
from utils.test_helpers import (
    enemy_called_riichi_helper,
    find_discard_option,
    make_meld,
    string_to_136_array,
    string_to_136_tile,
)


def test_tile_danger_genbutsu():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), False)
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="6")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, sou="6")


def test_tile_danger_and_impossible_wait_fourth_honor():
    enemy_seat = 1
    table = _create_table(
        enemy_seat, discards=string_to_136_array(honors="111"), riichi_tile=string_to_136_tile(honors="7")
    )
    player = table.player

    tiles = string_to_136_array(man="34678", pin="2356", honors="1555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.IMPOSSIBLE_WAIT, honors="1")


def test_tile_danger_and_impossible_wait_latest_tile_behind_kabe():
    enemy_seat = 1
    table = _create_table(
        enemy_seat, discards=string_to_136_array(sou="1112222"), riichi_tile=string_to_136_tile(honors="7")
    )
    player = table.player

    tiles = string_to_136_array(man="34678", pin="2356", honors="1555")
    tile = string_to_136_tile(sou="1")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.IMPOSSIBLE_WAIT, sou="1")


def test_tile_danger_and_honor_third():
    enemy_seat = 1
    table = _create_table(
        enemy_seat, discards=string_to_136_array(honors="11"), riichi_tile=string_to_136_tile(honors="7")
    )
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="1555")
    tile = string_to_136_tile(sou="8")

    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.HONOR_THIRD, honors="1")


def test_tile_danger_and_non_yakuhai_honor_second():
    enemy_seat = 1
    table = _create_table(
        enemy_seat, discards=string_to_136_array(honors="4"), riichi_tile=string_to_136_tile(honors="7")
    )
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="4555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.NON_YAKUHAI_HONOR_SECOND_EARLY, honors="4")


def test_tile_danger_and_non_yakuhai_honor_shonpai():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="4555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.NON_YAKUHAI_HONOR_SHONPAI_EARLY, honors="4")


def test_tile_danger_and_forms_bonus():
    enemy_seat = 1
    table = _create_table(
        enemy_seat, discards=string_to_136_array(man="9999"), riichi_tile=string_to_136_tile(honors="7")
    )
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
    table = _create_table(
        enemy_seat, discards=string_to_136_array(honors="6"), riichi_tile=string_to_136_tile(honors="7")
    )
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="5556")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.YAKUHAI_HONOR_SECOND_EARLY, honors="6")


def test_tile_danger_and_double_yakuhai_honor_second():
    enemy_seat = 1
    table = _create_table(
        enemy_seat, discards=string_to_136_array(honors="2"), riichi_tile=string_to_136_tile(honors="7")
    )
    table.round_wind_number = 5
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.DOUBLE_YAKUHAI_HONOR_SECOND_EARLY, honors="2")


def test_tile_danger_and_yakuhai_honor_shonpai():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="5556")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.YAKUHAI_HONOR_SHONPAI_EARLY, honors="6")


def test_tile_danger_and_double_yakuhai_honor_shonpai():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
    table.round_wind_number = 5
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="8")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.DOUBLE_YAKUHAI_HONOR_SHONPAI_EARLY, honors="2")


def test_tile_danger_and_terminal_suji_tiles():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
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
    table = _create_table(
        enemy_seat, discards=string_to_136_array(sou="2222"), riichi_tile=string_to_136_tile(honors="7")
    )
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = string_to_136_tile(sou="1")
    player.init_hand(tiles)
    player.draw_tile(tile)

    # 1 sou is shonpai
    _assert_discard(player, enemy_seat, TileDanger.SHONPAI_KABE_STRONG, sou="1")

    player.discard_tile()
    player.draw_tile(tile)
    # 1 sou is not shonpai anymore
    _assert_discard(player, enemy_seat, TileDanger.NON_SHONPAI_KABE_STRONG, sou="1")


def test_tile_danger_and_2_8_kabe_tiles():
    enemy_seat = 1
    table = _create_table(
        enemy_seat, discards=string_to_136_array(sou="44446666"), riichi_tile=string_to_136_tile(honors="7")
    )
    player = table.player

    tiles = string_to_136_array(sou="123789", pin="116", honors="2555")
    tile = string_to_136_tile(sou="5")
    player.init_hand(tiles)
    player.draw_tile(tile)

    # 5 sou is shonpai
    _assert_discard(player, enemy_seat, TileDanger.SHONPAI_KABE_STRONG, sou="5")

    player.discard_tile()
    player.draw_tile(tile)
    # 5 sou is not shonpai anymore
    _assert_discard(player, enemy_seat, TileDanger.NON_SHONPAI_KABE_STRONG, sou="5")

    # check all weak kabe
    _assert_discard(player, enemy_seat, TileDanger.SHONPAI_KABE_WEAK, sou="2")
    _assert_discard(player, enemy_seat, TileDanger.SHONPAI_KABE_WEAK, sou="3")
    _assert_discard(player, enemy_seat, TileDanger.SHONPAI_KABE_WEAK, sou="7")
    _assert_discard(player, enemy_seat, TileDanger.SHONPAI_KABE_WEAK, sou="8")

    player.discard_tile()
    player.draw_tile(string_to_136_tile(sou="2"))
    _assert_discard(player, enemy_seat, TileDanger.NON_SHONPAI_KABE_WEAK, sou="2")

    player.discard_tile()
    player.draw_tile(string_to_136_tile(sou="3"))
    _assert_discard(player, enemy_seat, TileDanger.NON_SHONPAI_KABE_WEAK, sou="3")

    player.discard_tile()
    player.draw_tile(string_to_136_tile(sou="7"))
    _assert_discard(player, enemy_seat, TileDanger.NON_SHONPAI_KABE_WEAK, sou="7")
    player.discard_tile()
    player.draw_tile(string_to_136_tile(sou="8"))
    _assert_discard(player, enemy_seat, TileDanger.NON_SHONPAI_KABE_WEAK, sou="8")


def test_tile_danger_and_2_8_suji_tiles():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
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


def test_tile_danger_and_suji_7_on_riichi():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(sou="4"))
    player = table.player

    tiles = string_to_136_array(sou="2378", pin="4", man="56", honors="233555")
    tile = string_to_136_tile(honors="3")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SUJI_37_ON_RIICHI, sou="7")


def test_tile_danger_and_suji_2_on_riichi():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(sou="5"))
    player = table.player

    tiles = string_to_136_array(sou="2378", pin="4", man="56", honors="233555")
    tile = string_to_136_tile(honors="3")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SUJI_28_ON_RIICHI, sou="8")


def test_tile_danger_and_suji_4_on_riichi():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(pin="7"))
    player = table.player

    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), False)

    tiles = string_to_136_array(sou="2378", pin="4", man="56", honors="233555")
    tile = string_to_136_tile(honors="3")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SUJI, pin="4")


def test_tile_danger_and_ryanmen_wait():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
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
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
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
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="2555")
    tile = FIVE_RED_SOU
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.DORA_BONUS, sou="5")


@pytest.mark.skip("Skipped until danger values tuning is finished")
def test_tile_total_danger():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
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

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="3"), False)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat

    tiles = string_to_136_array(man="11134", pin="1569", honors="2555")
    tile = string_to_136_tile(sou="4")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, man="1")
    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, pin="9")
    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, honors="2")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, pin="5")


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

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat

    tiles = string_to_136_array(man="11134", pin="1569", honors="2555")
    tile = string_to_136_tile(sou="4")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, man="3")
    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, sou="4")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, pin="5")


def test_tile_danger_against_toitoi_threat():
    table = Table()
    table.add_dora_indicator(string_to_136_tile(pin="1"))
    player = table.player

    enemy_seat = 1
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, pin="222"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, honors="444"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, sou="999"))

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="3"), False)

    table.add_dora_indicator(string_to_136_tile(pin="1"))

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat

    # let's make 2 man impossible to wait in toitoi
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="2"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="2"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="2"), False)

    tiles = string_to_136_array(man="11134", pin="1569", honors="2555")
    tile = string_to_136_tile(man="2")
    player.init_hand(tiles)
    player.draw_tile(tile)

    _assert_discard(player, enemy_seat, TileDanger.SAFE_AGAINST_THREATENING_HAND, man="2")


def test_tile_danger_matagi_suji_pattern():
    enemy_seat = 1
    table = _create_table(enemy_seat, discards=[], riichi_tile=string_to_136_tile(honors="7"))
    player = table.player

    tiles = string_to_136_array(man="11134", pin="1156", honors="255", sou="4")
    tile = string_to_136_tile(sou="5")
    player.init_hand(tiles)
    player.draw_tile(tile)

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), is_tsumogiri=False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="5"), is_tsumogiri=True)

    # it is too early for matagi check
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_MATAGI_SUJI, sou="5")

    table.add_discarded_tile(enemy_seat, string_to_136_tile(honors="6"), is_tsumogiri=True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(honors="6"), is_tsumogiri=True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), is_tsumogiri=False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), is_tsumogiri=False)

    # 8s in discard, so 5s is not matagi suji
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_MATAGI_SUJI, sou="5")
    # 4-7 is still matagi
    _assert_discard(player, enemy_seat, TileDanger.BONUS_MATAGI_SUJI, sou="4")

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), is_tsumogiri=True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="6"), is_tsumogiri=False)

    # 4s is not matagi anymore, because 6p is latest discard from the hand
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_MATAGI_SUJI, sou="4")

    table.add_discarded_tile(enemy_seat, string_to_136_tile(honors="6"), is_tsumogiri=True)

    # 4s is matagi again, because it is late stage and we are checking two latest discards from hand
    _assert_discard(player, enemy_seat, TileDanger.BONUS_MATAGI_SUJI, sou="4")


def test_tile_danger_aidayonken_pattern():
    enemy_seat = 1
    table = Table()
    table.has_aka_dora = True
    player = table.player

    tiles = string_to_136_array(man="11345", pin="11256", honors="5", sou="25")
    tile = string_to_136_tile(sou="5")
    player.init_hand(tiles)
    player.draw_tile(tile)

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="2"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="6"), True)

    enemy_called_riichi_helper(table, enemy_seat)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(honors="7"), False)

    # there is 2 in enemy discard, in that case we don't want to add danger for 5
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, sou="5")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, sou="2")

    # enemy didn't discard suji discards let's add danger for 2-5 in that case
    _assert_discard(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, pin="2")
    _assert_discard(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, pin="5")

    # to be sure that we are not checking other suit
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, man="5")


# aidayonken should not matter after riichi
def test_tile_danger_aidayonken_after_riichi():
    enemy_seat = 1
    table = Table()
    table.has_aka_dora = True
    player = table.player

    tiles = string_to_136_array(man="11345", pin="11256", honors="5", sou="25")
    tile = string_to_136_tile(sou="5")
    player.init_hand(tiles)
    player.draw_tile(tile)

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), True)

    enemy_called_riichi_helper(table, enemy_seat)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(honors="7"), False)

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="2"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="6"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="6"), True)

    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, sou="5")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, sou="2")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, pin="2")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, pin="5")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_AIDAYONKEN, man="5")


def test_tile_danger_early_discard_early():
    enemy_seat = 1
    table = Table()
    table.has_aka_dora = True
    player = table.player

    tiles = string_to_136_array(man="11345", pin="11289", honors="5", sou="19")
    tile = string_to_136_tile(man="9")
    player.init_hand(tiles)
    player.draw_tile(tile)

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="2"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="7"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), True)

    enemy_called_riichi_helper(table, enemy_seat, string_to_136_tile(pin="4"))

    # too early to judge about early discards
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_28, sou="1")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_5, sou="9")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_37, pin="8")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_37, pin="9")


def test_tile_danger_early_discard_normal():
    enemy_seat = 1
    table = Table()
    table.has_aka_dora = True
    player = table.player

    tiles = string_to_136_array(man="11345", pin="11289", honors="5", sou="19")
    tile = string_to_136_tile(man="9")
    player.init_hand(tiles)
    player.draw_tile(tile)

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="2"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="7"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="3"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="4"), False)
    enemy_called_riichi_helper(table, enemy_seat)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="2"), False)

    # now that looks like 1 sou is not too dangerous and 9 sou is on the contrary very dangerous
    _assert_discard(player, enemy_seat, TileDanger.BONUS_EARLY_28, sou="1")
    _assert_discard(player, enemy_seat, TileDanger.BONUS_EARLY_5, sou="9")
    _assert_discard(player, enemy_seat, TileDanger.BONUS_EARLY_37, pin="8")
    _assert_discard(player, enemy_seat, TileDanger.BONUS_EARLY_37, pin="9")

    # check it's not vice versa
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_5, sou="1")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_28, sou="9")

    # to be sure that we are not checking other suit
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_28, man="9")


def test_tile_danger_early_discard_early_riichi():
    enemy_seat = 1
    table = Table()
    table.has_aka_dora = True
    player = table.player

    tiles = string_to_136_array(man="11345", pin="11289", honors="5", sou="19")
    tile = string_to_136_tile(man="9")
    player.init_hand(tiles)
    player.draw_tile(tile)

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="2"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="7"), True)
    enemy_called_riichi_helper(table, enemy_seat)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="5"), False)

    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="3"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="4"), True)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="2"), True)

    # too early to judge about early discards, despite lots of them, we only care about those
    # before riichi
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_28, sou="1")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_37, pin="8")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_37, pin="9")
    _assert_discard_not_equal(player, enemy_seat, TileDanger.BONUS_EARLY_5, sou="9")


def _create_table(enemy_seat, discards, riichi_tile):
    table = Table()
    table.has_aka_dora = True
    for discard in discards:
        table.add_discarded_tile(0, discard, False)
    enemy_called_riichi_helper(table, enemy_seat, riichi_tile)
    return table


def _assert_discard_not_equal(player, enemy_seat, tile_danger, sou="", pin="", man="", honors=""):
    _assert_discard(player, enemy_seat, tile_danger, False, sou, pin, man, honors)


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
