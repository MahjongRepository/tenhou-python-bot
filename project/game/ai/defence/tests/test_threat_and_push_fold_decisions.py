from game.table import Table
from mahjong.constants import FIVE_RED_MAN
from utils.decisions_logger import MeldPrint
from utils.test_helpers import find_discard_option, string_to_136_array, string_to_136_tile

from project.utils.test_helpers import make_meld


def test_calculate_our_hand_cost():
    table = _make_table()
    player = table.player
    enemy_seat = 2
    table.add_called_riichi_step_one(enemy_seat)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="9"), True)

    tiles = string_to_136_array(sou="234678", pin="23478", man="22")
    tile = string_to_136_tile(honors="1")
    player.init_hand(tiles)
    player.draw_tile(tile)

    discard_option = find_discard_option(player, honors="1")
    assert discard_option.danger.weighted_cost == 6128


def test_calculate_our_hand_cost_1_shanten():
    table = _make_table()
    player = table.player
    enemy_seat = 2

    table.has_open_tanyao = True
    table.has_aka_dora = False

    table.add_called_riichi_step_one(enemy_seat)

    tiles = string_to_136_array(sou="22245677", pin="145", man="67")

    tile = string_to_136_tile(honors="1")
    player.init_hand(tiles)
    player.add_called_meld(make_meld(MeldPrint.PON, sou="222"))
    player.draw_tile(tile)

    discard_option = find_discard_option(player, honors="1")
    cost = discard_option.average_second_level_cost

    assert cost == 1500

    table.add_dora_indicator(string_to_136_tile(sou="6"))
    discard_option = find_discard_option(player, honors="1")
    cost = discard_option.average_second_level_cost

    assert cost == 5850

    table.add_dora_indicator(string_to_136_tile(pin="2"))
    discard_option = find_discard_option(player, honors="1")
    cost = discard_option.average_second_level_cost

    assert cost == 8737


def test_calculate_our_hand_cost_1_shanten_karaten():
    table = _make_table()
    player = table.player
    enemy_seat = 2

    table.has_open_tanyao = True
    table.has_aka_dora = False

    table.add_called_riichi_step_one(enemy_seat)

    tiles = string_to_136_array(sou="22245677", pin="145", man="67")

    tile = string_to_136_tile(honors="1")
    player.init_hand(tiles)
    player.add_called_meld(make_meld(MeldPrint.PON, sou="222"))
    player.draw_tile(tile)

    # average cost should not change because of less waits
    for _ in range(0, 4):
        table.add_discarded_tile(1, string_to_136_tile(pin="3"), False)

    discard_option = find_discard_option(player, honors="1")
    cost = discard_option.average_second_level_cost

    assert cost == 1500

    # average cost should become 0 for karaten, even if just one of the waits is dead
    for _ in range(0, 4):
        table.add_discarded_tile(1, string_to_136_tile(pin="6"), False)

    discard_option = find_discard_option(player, honors="1")
    cost = discard_option.average_second_level_cost

    assert cost == 0

    # nothing should crash in case all waits are dead as well
    for _ in range(0, 4):
        table.add_discarded_tile(1, string_to_136_tile(man="5"), False)
        table.add_discarded_tile(1, string_to_136_tile(man="8"), False)

    discard_option = find_discard_option(player, honors="1")
    cost = discard_option.average_second_level_cost

    assert cost == 0


def test_dont_open_bad_hand_if_there_are_expensive_threat():
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(man="4"))
    player = table.player
    player.round_step = 10
    table.has_open_tanyao = True
    table.has_aka_dora = True

    enemy_seat = 1
    table.add_called_riichi_step_one(enemy_seat)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(honors="4"), True)

    tiles = string_to_136_array(sou="226", pin="2469", man="3344", honors="4") + [FIVE_RED_MAN]
    player.init_hand(tiles)

    # cheap enemy tempai, but this meld is garbage, let's not push
    tile = string_to_136_array(man="4444")[2]
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is None

    # cheap enemy tempai, and good chi, let's take this meld
    tile = string_to_136_tile(man="2")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, honors="1111"))
    # enemy hand is more expensive now (12000)
    # in this case let's not open this hand
    tile = string_to_136_tile(man="2")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is None


def test_dont_open_bad_hand_if_there_are_multiple_threats():
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(man="4"))
    player = table.player
    player.round_step = 10
    table.has_open_tanyao = True
    table.has_aka_dora = True

    table.add_called_riichi_step_one(1)
    table.add_discarded_tile(1, string_to_136_tile(honors="4"), True)

    table.add_called_riichi_step_one(2)
    table.add_discarded_tile(2, string_to_136_tile(honors="4"), True)

    tiles = string_to_136_array(sou="22499", pin="27", man="3344", honors="4") + [FIVE_RED_MAN]
    player.init_hand(tiles)
    tile = string_to_136_tile(man="4")

    # there are multiple threats with (3900+) hands
    # let's not push in that case
    meld, _ = player.try_to_call_meld(tile, False)
    assert meld is None


def _make_table():
    table = Table()
    table.init_round(1, 0, 0, string_to_136_tile(honors="4"), 0, [250, 250, 250, 250])
    # with that we don't have daburi anymore
    table.player.round_step = 1
    return table
