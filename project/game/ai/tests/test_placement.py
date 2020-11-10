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

    placement = player.ai.placement.get_placement_evaluation()
    assert placement == Placement.VERY_COMFORTABLE_FIRST
