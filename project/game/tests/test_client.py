from game.client import Client
from utils.decisions_logger import MeldPrint


def test_discard_tile():
    client = Client()

    client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])
    tiles = [1, 22, 3, 4, 43, 6, 7, 8, 9, 55, 11, 12, 13, 99]
    client.table.player.init_hand(tiles)

    assert len(client.table.player.tiles) == 14
    assert client.table.count_of_remaining_tiles == 70

    tile = client.player.discard_tile()

    assert len(client.table.player.tiles) == 13
    assert len(client.table.player.discards) == 1
    assert not (tile in client.table.player.tiles)


def test_call_meld_closed_kan():
    client = Client()

    client.table.init_round(0, 0, 0, 100, 0, [0, 0, 0, 0])
    assert client.table.count_of_remaining_tiles == 70

    meld = MeldPrint()
    client.table.add_called_meld(0, meld)

    assert len(client.player.melds) == 1
    assert client.table.count_of_remaining_tiles == 71

    client.player.tiles = [0]
    meld = MeldPrint()
    meld.type = MeldPrint.KAN
    # closed kan
    meld.tiles = [0, 1, 2, 3]
    meld.called_tile = None
    meld.opened = False
    client.table.add_called_meld(0, meld)

    assert len(client.player.melds) == 2
    # kan was closed, so -1
    assert client.table.count_of_remaining_tiles == 70


def test_call_meld_kan_from_player():
    client = Client()

    client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])
    assert client.table.count_of_remaining_tiles == 70

    meld = MeldPrint()
    client.table.add_called_meld(0, meld)

    assert len(client.player.melds) == 1
    assert client.table.count_of_remaining_tiles == 71

    client.player.tiles = [0]
    meld = MeldPrint()
    meld.type = MeldPrint.KAN
    # closed kan
    meld.tiles = [0, 1, 2, 3]
    meld.called_tile = 0
    meld.opened = True
    client.table.add_called_meld(0, meld)

    assert len(client.player.melds) == 2
    # kan was called from another player, total number of remaining tiles stays the same
    assert client.table.count_of_remaining_tiles == 71


def test_enemy_discard():
    client = Client()
    client.table.init_round(0, 0, 0, 0, 0, [0, 0, 0, 0])

    assert client.table.count_of_remaining_tiles == 70

    client.table.add_discarded_tile(1, 10, False)

    assert client.table.count_of_remaining_tiles == 69
