from game.table import Table
from utils.decisions_logger import MeldPrint
from utils.test_helpers import find_discard_option, string_to_136_array, string_to_136_tile

from project.utils.test_helpers import make_meld


def test_calculate_our_hand_cost():
    table = Table()
    player = table.player
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="9"), True)

    tiles = string_to_136_array(sou="234678", pin="23478", man="22")
    tile = string_to_136_tile(honors="1")
    player.init_hand(tiles)
    player.draw_tile(tile)

    discard_option = find_discard_option(player, honors="1")
    assert discard_option.danger.weighted_cost == 4557


def test_calculate_our_hand_cost_1_shanten():
    table = Table()
    player = table.player
    enemy_seat = 2

    table.has_open_tanyao = True
    table.has_aka_dora = False

    table.add_called_riichi(enemy_seat)

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

    assert cost == 8737.5


def test_calculate_our_hand_cost_1_shanten_karaten():
    table = Table()
    player = table.player
    enemy_seat = 2

    table.has_open_tanyao = True
    table.has_aka_dora = False

    table.add_called_riichi(enemy_seat)

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
