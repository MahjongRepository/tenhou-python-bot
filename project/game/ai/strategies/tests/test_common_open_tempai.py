from game.table import Table
from utils.test_helpers import string_to_136_array, string_to_136_tile, tiles_to_string


def test_get_common_tempai_sanshoku():
    table = Table()

    table.add_dora_indicator(string_to_136_tile(man="8"))

    tiles = string_to_136_array(man="13999", sou="123", pin="12899")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "123p"


def test_get_common_tempai_honro():
    table = Table()

    tiles = string_to_136_array(man="11999", sou="112", pin="99", honors="333")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="9")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "999p"


def test_get_common_tempai_and_0_ukeire_crash():
    """
    Checks that we don't have crash anymore when bot tried to open hand with 0 ukeire
    :return:
    """
    table = Table()
    table.add_discarded_tile(1, string_to_136_tile(sou="1"), True)
    table.add_discarded_tile(1, string_to_136_tile(sou="1"), True)
    table.add_discarded_tile(1, string_to_136_tile(man="1"), True)
    table.add_discarded_tile(1, string_to_136_tile(man="1"), True)

    tiles = string_to_136_array(man="11999", sou="116", pin="99", honors="333")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="9")
    meld, _ = table.player.try_to_call_meld(tile, False)
    # no ukeire, no reason to open hand
    assert meld is None


def test_get_common_tempai_sandoko():
    table = Table()

    table.add_dora_indicator(string_to_136_tile(man="1"))

    tiles = string_to_136_array(man="222", sou="2278", pin="222899")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(sou="2")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "222s"


def test_get_common_tempai_bad_atodzuke():
    table = Table()

    tiles = string_to_136_array(man="23789", sou="3", pin="99", honors="33444")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="9")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is None


def test_get_common_tempai_no_yaku():
    table = Table()

    tiles = string_to_136_array(man="234999", sou="112", pin="55", honors="333")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="9")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is None
