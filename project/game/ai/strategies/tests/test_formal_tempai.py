from game.ai.strategies.formal_tempai import FormalTempaiStrategy
from game.ai.strategies.main import BaseStrategy
from game.table import Table
from mahjong.tile import Tile
from utils.decisions_logger import MeldPrint
from utils.test_helpers import make_meld, string_to_136_array, string_to_136_tile, tiles_to_string


def test_should_activate_strategy():
    table = Table()
    table.player.dealer_seat = 3

    strategy = FormalTempaiStrategy(BaseStrategy.FORMAL_TEMPAI, table.player)

    tiles = string_to_136_array(sou="12355689", man="89", pin="339")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    # Let's move to 10th round step
    for _ in range(0, 10):
        table.player.add_discarded_tile(Tile(0, False))

    assert strategy.should_activate_strategy(table.player.tiles) is False

    # Now we move to 11th turn, we have 2 shanten and no doras,
    # we should go for formal tempai
    table.player.add_discarded_tile(Tile(0, True))
    assert strategy.should_activate_strategy(table.player.tiles) is True


def test_get_tempai():
    table = Table()
    table.player.dealer_seat = 3

    tiles = string_to_136_array(man="2379", sou="4568", pin="22299")
    table.player.init_hand(tiles)

    # Let's move to 15th round step
    for _ in range(0, 15):
        table.player.add_discarded_tile(Tile(0, False))

    tile = string_to_136_tile(man="8")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "789m"

    # reinit hand with meld
    tiles = string_to_136_array(man="23789", sou="4568", pin="22299")
    table.player.init_hand(tiles)
    table.player.add_called_meld(meld)

    tile_to_discard, _ = table.player.discard_tile()
    assert tiles_to_string([tile_to_discard]) == "8s"


def test_dont_meld_agari():
    """
    We shouldn't open when we are already in tempai expect for some special cases
    """
    table = Table()
    table.player.dealer_seat = 3

    strategy = FormalTempaiStrategy(BaseStrategy.FORMAL_TEMPAI, table.player)

    tiles = string_to_136_array(man="2379", sou="4568", pin="22299")
    table.player.init_hand(tiles)

    # Let's move to 15th round step
    for _ in range(0, 15):
        table.player.add_discarded_tile(Tile(0, False))

    assert strategy.should_activate_strategy(table.player.tiles) is True

    tiles = string_to_136_array(man="23789", sou="456", pin="22299")
    table.player.init_hand(tiles)

    meld = make_meld(MeldPrint.CHI, man="789")
    table.player.add_called_meld(meld)

    tile = string_to_136_tile(man="4")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None
