import pytest
from game.ai.strategies.honitsu import HonitsuStrategy
from game.ai.strategies.main import BaseStrategy
from game.table import Table
from utils.decisions_logger import MeldPrint
from utils.test_helpers import make_meld, string_to_136_array, string_to_136_tile, tiles_to_string


def test_should_activate_strategy():
    table = Table()
    player = table.player
    strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)

    table.add_dora_indicator(string_to_136_tile(pin="1"))
    table.add_dora_indicator(string_to_136_tile(honors="5"))

    tiles = string_to_136_array(sou="12355", man="12389", honors="123")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is False

    # many tiles in one suit and yakuhai pair, but still many useless winds
    tiles = string_to_136_array(sou="12355", man="23", pin="68", honors="2355")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is False

    # many tiles in one suit and yakuhai pair and another honor pair, so
    # now this is honitsu
    tiles = string_to_136_array(sou="12355", man="238", honors="22355")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is True

    # same conditions, but ready suit with dora in another suit, so no honitsu
    tiles = string_to_136_array(sou="12355", pin="234", honors="22355")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is False

    # same conditions, but we have a pon of yakuhai doras, we shouldn't
    # force honitsu with this hand
    tiles = string_to_136_array(sou="12355", pin="238", honors="22666")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is False

    # if we have a complete set with dora, we shouldn't go for honitsu
    tiles = string_to_136_array(sou="11123688", pin="123", honors="55")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is False

    # even if the set may be interpreted as two forms
    tiles = string_to_136_array(sou="1223688", pin="2334", honors="55")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is False

    # even if the set may be interpreted as two forms v2
    tiles = string_to_136_array(sou="1223688", pin="2345", honors="55")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is False

    # if we have a long form with dora, we shouldn't go for honitsu
    tiles = string_to_136_array(sou="1223688", pin="2333", honors="55")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is False


def test_suitable_tiles():
    table = Table()
    player = table.player
    strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)

    tiles = string_to_136_array(sou="12355", man="238", honors="23455")
    player.init_hand(tiles)
    assert strategy.should_activate_strategy(player.tiles) is True

    tile = string_to_136_tile(man="1")
    assert strategy.is_tile_suitable(tile) is False

    tile = string_to_136_tile(pin="1")
    assert strategy.is_tile_suitable(tile) is False

    tile = string_to_136_tile(sou="1")
    assert strategy.is_tile_suitable(tile) is True

    tile = string_to_136_tile(honors="1")
    assert strategy.is_tile_suitable(tile) is True


def test_open_hand_and_discard_tiles_logic():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="112235589", man="23", honors="66")
    player.init_hand(tiles)

    # we don't need to call meld even if it improves our hand,
    # because we are aim for honitsu or pinfu
    tile = string_to_136_tile(man="1")
    meld, _ = player.try_to_call_meld(tile, False)
    assert meld is None

    # any honor tile is suitable
    tile = string_to_136_tile(honors="6")
    meld, discard_option = player.try_to_call_meld(tile, False)
    assert meld is not None
    assert tiles_to_string([discard_option.tile_to_discard_136]) == "2m"

    tile = string_to_136_tile(man="1")
    player.draw_tile(tile)
    tile_to_discard, _ = player.discard_tile()

    # we are in honitsu mode, so we should discard man suits
    assert tiles_to_string([tile_to_discard]) == "1m"


def test_riichi_and_tiles_from_another_suit_in_the_hand():
    table = Table()
    player = table.player
    player.scores = 25000
    table.count_of_remaining_tiles = 100

    tiles = string_to_136_array(man="33345678", pin="22", honors="155")
    player.init_hand(tiles)

    player.draw_tile(string_to_136_tile(man="9"))
    tile_to_discard, _ = player.discard_tile()

    # we don't need to go for honitsu here
    # we already in tempai
    assert tiles_to_string([tile_to_discard]) == "1z"


def test_discard_not_needed_winds():
    table = Table()
    player = table.player
    player.scores = 25000
    table.count_of_remaining_tiles = 100

    tiles = string_to_136_array(man="24", pin="4", sou="12344668", honors="36")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(sou="5"))

    table.add_discarded_tile(1, string_to_136_tile(honors="3"), False)
    table.add_discarded_tile(1, string_to_136_tile(honors="3"), False)
    table.add_discarded_tile(1, string_to_136_tile(honors="3"), False)

    tile_to_discard, _ = player.discard_tile()

    # west was discarded three times, we don't need it
    assert tiles_to_string([tile_to_discard]) == "3z"


def test_discard_not_effective_tiles_first():
    table = Table()
    player = table.player
    player.scores = 25000
    table.count_of_remaining_tiles = 100

    tiles = string_to_136_array(man="33", pin="12788999", sou="5", honors="77")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(honors="6"))
    tile_to_discard, _ = player.discard_tile()

    assert tiles_to_string([tile_to_discard]) == "5s"


def test_discard_not_effective_tiles_first_not_honitsu():
    table = Table()
    player = table.player
    player.scores = 25000
    table.count_of_remaining_tiles = 100

    tiles = string_to_136_array(man="33", pin="12788999", sou="5", honors="23")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(honors="6"))
    tile_to_discard, _ = player.discard_tile()

    # this is not really a honitsu
    assert tiles_to_string([tile_to_discard]) == "2z" or tiles_to_string([tile_to_discard]) == "3z"


def test_open_yakuhai_same_shanten():
    table = Table()
    player = table.player
    player.scores = 25000
    table.count_of_remaining_tiles = 100

    tiles = string_to_136_array(man="34556778", pin="3", sou="78", honors="77")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.CHI, man="345")
    player.add_called_meld(meld)

    strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    tile = string_to_136_tile(honors="7")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "777z"


def test_open_hand_and_not_go_for_chiitoitsu():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="1122559", honors="134557")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(pin="4"))

    tile, _ = player.discard_tile()
    assert tiles_to_string([tile]) == "4p"

    tile = string_to_136_tile(honors="5")
    meld, _ = player.try_to_call_meld(tile, False)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "555z"


@pytest.mark.skip("Skipped, needs strategies refactoring, ref #153")
def test_open_hand_and_not_go_for_atodzuke_yakuhai():
    table = Table()
    # dora here to activate honitsu strategy
    table.add_dora_indicator(string_to_136_tile(sou="9"))
    player = table.player
    player.seat = 1

    tiles = string_to_136_array(sou="1112345678", honors="557")
    player.init_hand(tiles)
    tile = string_to_136_array(sou="1111")[3]
    meld, _ = player.try_to_call_meld(tile, False)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "111s"


def test_open_suit_same_shanten():
    table = Table()
    player = table.player
    player.scores = 25000
    table.count_of_remaining_tiles = 100

    tiles = string_to_136_array(man="1134556", pin="3", sou="78", honors="777")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.CHI, man="345")
    player.add_called_meld(meld)

    strategy = HonitsuStrategy(BaseStrategy.HONITSU, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    tile = string_to_136_tile(man="1")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "111m"
