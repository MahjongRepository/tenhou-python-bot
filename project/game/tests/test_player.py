from game.table import Table
from mahjong.constants import EAST, NORTH, SOUTH, WEST
from utils.decisions_logger import MeldPrint
from utils.test_helpers import make_meld, string_to_136_array


def test_can_call_riichi_and_tempai():
    table = Table()
    player = table.player

    player.in_tempai = False
    player.in_riichi = False
    player.scores = 2000
    player.table.count_of_remaining_tiles = 40

    assert player.formal_riichi_conditions() is False

    player.in_tempai = True

    assert player.formal_riichi_conditions() is True


def test_can_call_riichi_and_already_in_riichi():
    table = Table()
    player = table.player

    player.in_tempai = True
    player.in_riichi = True
    player.scores = 2000
    player.table.count_of_remaining_tiles = 40

    assert player.formal_riichi_conditions() is False

    player.in_riichi = False

    assert player.formal_riichi_conditions() is True


def test_can_call_riichi_and_scores():
    table = Table()
    player = table.player

    player.in_tempai = True
    player.in_riichi = False
    player.scores = 0
    player.table.count_of_remaining_tiles = 40

    assert player.formal_riichi_conditions() is False

    player.scores = 1000

    assert player.formal_riichi_conditions() is True


def test_can_call_riichi_and_remaining_tiles():
    table = Table()
    player = table.player

    player.in_tempai = True
    player.in_riichi = False
    player.scores = 2000
    player.table.count_of_remaining_tiles = 3

    assert player.formal_riichi_conditions() is False

    player.table.count_of_remaining_tiles = 5

    assert player.formal_riichi_conditions() is True


def test_can_call_riichi_and_open_hand():
    table = Table()
    player = table.player

    player.in_tempai = True
    player.in_riichi = False
    player.scores = 2000
    player.melds = [MeldPrint()]
    player.table.count_of_remaining_tiles = 40

    assert player.formal_riichi_conditions() is False

    player.melds = []

    assert player.formal_riichi_conditions() is True


def test_players_wind():
    table = Table()
    player = table.player

    dealer_seat = 0
    table.init_round(0, 0, 0, 0, dealer_seat, [])
    assert player.player_wind == EAST
    assert table.get_player(1).player_wind == SOUTH

    dealer_seat = 1
    table.init_round(0, 0, 0, 0, dealer_seat, [])
    assert player.player_wind == NORTH
    assert table.get_player(1).player_wind == EAST

    dealer_seat = 2
    table.init_round(0, 0, 0, 0, dealer_seat, [])
    assert player.player_wind == WEST
    assert table.get_player(1).player_wind == NORTH

    dealer_seat = 3
    table.init_round(0, 0, 0, 0, dealer_seat, [])
    assert player.player_wind == SOUTH
    assert table.get_player(1).player_wind == WEST


def test_player_called_meld_and_closed_hand():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="123678", pin="3599", honors="555")
    player.init_hand(tiles)

    assert len(player.closed_hand) == 13

    player.add_called_meld(make_meld(MeldPrint.PON, honors="555"))

    assert len(player.closed_hand) == 10
