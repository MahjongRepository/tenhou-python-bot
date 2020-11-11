from game.ai.placement import Placement
from game.table import Table


def test_placement_evaluation():
    table = Table()
    player = table.player

    # very comfortable first
    player.scores = 82000
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 6000

    placement = player.ai.placement.get_placement_evaluation(player.ai.placement._get_current_placement())
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
