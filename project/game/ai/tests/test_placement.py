from game.ai.placement import Placement
from game.table import Table
from utils.decisions_logger import MeldPrint
from utils.test_helpers import make_meld, string_to_136_array, string_to_136_tile


def test_placement_evaluation():
    table = Table()
    player = table.player

    # very comfortable first
    player.scores = 82000
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 6000

    placement = player.ai.placement._get_placement_evaluation(player.ai.placement._get_current_placement())
    assert placement == Placement.VERY_COMFORTABLE_FIRST


def test_placement():
    table = Table()
    player = table.player

    player.scores = 82000
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 6000

    placement = player.ai.placement._get_current_placement()
    assert placement["place"] == 1
    assert placement["diff_with_1st"] == 0
    assert placement["diff_with_2nd"] == 76000
    assert placement["diff_with_3rd"] == 76000
    assert placement["diff_with_4th"] == 76000
    assert placement["diff_with_next_up"] == 0
    assert placement["diff_with_next_down"] == 76000

    player.scores = 22000
    i = -1
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 24000 + i * 6000
            i += 1

    placement = player.ai.placement._get_current_placement()
    assert placement["place"] == 3
    assert placement["diff_with_1st"] == 8000
    assert placement["diff_with_2nd"] == 2000
    assert placement["diff_with_3rd"] == 0
    assert placement["diff_with_4th"] == 4000
    assert placement["diff_with_next_up"] == 2000
    assert placement["diff_with_next_down"] == 4000

    player.scores = 1000
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 33000

    placement = player.ai.placement._get_current_placement()
    assert placement["place"] == 4
    assert placement["diff_with_1st"] == 32000
    assert placement["diff_with_2nd"] == 32000
    assert placement["diff_with_3rd"] == 32000
    assert placement["diff_with_4th"] == 0
    assert placement["diff_with_next_up"] == 32000
    assert placement["diff_with_next_down"] == 0


def test_minimal_cost():
    table = Table()
    player = table.player

    # orasu
    table.round_wind_number = 7

    player.scores = 22000
    i = -1
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 24000 + i * 6000
            i += 1

    minimal_cost = player.ai.placement.get_minimal_cost_needed()
    assert minimal_cost == 0

    player.scores = 1000
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 33000

    minimal_cost = player.ai.placement.get_minimal_cost_needed()
    assert minimal_cost == 32000


def test_skip_ron():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    # 1900 to 3rd place
    player.scores = 20100
    assert table.players[0] == player
    table.players[1].scores = 22000
    table.players[2].scores = 26000
    table.players[3].scores = 30900

    minimal_cost = player.ai.placement.get_minimal_cost_needed()
    assert minimal_cost == 1900

    tiles = string_to_136_array(man="23488", sou="34678", pin="567")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, pin="567"))
    table.player.round_step = 14

    # we should not call ron 1000 from 2nd place as it leaves us on 4th
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 2)

    # ron 2000 from 2nd place is ok, it's enough to get to 3rd
    assert player.should_call_win(string_to_136_tile(sou="2"), False, 2)

    # ron 1000 from 3rd place is ok too
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)

    # ron 1000 from 1st place is ok too as it moves us to west round
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 3)

    # ron 2000 from 1st place is ok, checking just to be sure
    assert player.should_call_win(string_to_136_tile(sou="2"), False, 3)


def test_take_ron_for_west():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    tiles = string_to_136_array(man="23488", sou="34678", pin="567")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, pin="567"))
    table.player.round_step = 14

    player.scores = 20100
    assert table.players[0] == player
    table.players[1].scores = 22000
    table.players[2].scores = 26000
    table.players[3].scores = 29900

    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 2)
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 3)

    player.scores = 20100
    assert table.players[0] == player
    table.players[1].scores = 22000
    table.players[2].scores = 30100
    table.players[3].scores = 31000

    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 2)
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 3)
