from game.ai.helpers.defence import TileDanger
from game.table import Table
from utils.test_helpers import find_discard_option, string_to_136_array, string_to_136_tile


def test_defence_and_impossible_wait():
    enemy_seat = 1

    table = Table()
    player = table.player

    table.add_discarded_tile(0, string_to_136_tile(honors="1"), False)
    table.add_discarded_tile(0, string_to_136_tile(honors="1"), False)
    table.add_discarded_tile(0, string_to_136_tile(honors="1"), False)

    table.add_called_riichi(enemy_seat)

    tiles = string_to_136_array(man="34678", pin="2356", honors="1555")
    tile = string_to_136_tile(sou="8")

    player.init_hand(tiles)
    player.draw_tile(tile)

    discard_options, _ = player.ai.hand_builder.find_discard_options(player.tiles, player.closed_hand, player.melds)

    discard_options, _ = player.ai.defence.check_threat_and_mark_tiles_danger(discard_options)

    discard_option = find_discard_option(discard_options, honors="1")
    assert len(discard_option.danger.values[enemy_seat]) == 1
    assert discard_option.danger.get_total_danger(enemy_seat) == TileDanger.IMPOSSIBLE_WAIT["value"]


def test_defence_and_third_honor():
    enemy_seat = 1

    table = Table()
    player = table.player

    table.add_discarded_tile(0, string_to_136_tile(honors="1"), False)
    table.add_discarded_tile(0, string_to_136_tile(honors="1"), False)

    table.add_called_riichi(enemy_seat)

    tiles = string_to_136_array(man="11134", pin="1156", honors="1555")
    tile = string_to_136_tile(sou="8")

    player.init_hand(tiles)
    player.draw_tile(tile)

    discard_options, _ = player.ai.hand_builder.find_discard_options(player.tiles, player.closed_hand, player.melds)
    discard_options, _ = player.ai.defence.check_threat_and_mark_tiles_danger(discard_options)
    discard_option = find_discard_option(discard_options, honors="1")
    assert len(discard_option.danger.values[enemy_seat]) == 1
    assert discard_option.danger.get_total_danger(enemy_seat) == TileDanger.HONOR_THIRD["value"]
