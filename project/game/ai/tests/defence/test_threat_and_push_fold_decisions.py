from game.table import Table
from utils.test_helpers import find_discard_option, string_to_136_array, string_to_136_tile


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
