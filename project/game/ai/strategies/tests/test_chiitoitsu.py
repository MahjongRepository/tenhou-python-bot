from game.ai.strategies.main import BaseStrategy
from game.table import Table
from utils.test_helpers import string_to_136_array, string_to_136_tile, tiles_to_string


def test_should_activate_strategy():
    table = Table()
    player = table.player

    # obvious chiitoitsu, let's activate
    tiles = string_to_136_array(sou="2266", man="3399", pin="289", honors="11")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(honors="6"))

    # less than 5 pairs, don't activate
    tiles = string_to_136_array(sou="2266", man="3389", pin="289", honors="11")
    player.draw_tile(string_to_136_tile(honors="6"))
    player.init_hand(tiles)

    # 5 pairs, but we are already tempai, let's no consider this hand as chiitoitsu
    tiles = string_to_136_array(sou="234", man="223344", pin="5669")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(pin="5"))
    player.discard_tile()

    tiles = string_to_136_array(sou="234", man="22334455669")
    player.init_hand(tiles)


def test_dont_call_meld():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="112234", man="2334499")
    player.init_hand(tiles)

    tile = string_to_136_tile(man="9")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is None


def test_keep_chiitoitsu_tempai():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="113355", man="22669", pin="99")
    player.init_hand(tiles)

    player.draw_tile(string_to_136_tile(man="6"))

    discard, _ = player.discard_tile()
    assert tiles_to_string([discard]) == "6m"


def test_5_pairs_yakuhai_not_chiitoitsu():
    table = Table()
    player = table.player

    table.add_dora_indicator(string_to_136_tile(sou="9"))
    table.add_dora_indicator(string_to_136_tile(sou="1"))

    tiles = string_to_136_array(sou="112233", pin="16678", honors="66")
    player.init_hand(tiles)

    tile = string_to_136_tile(honors="6")
    meld, _ = player.try_to_call_meld(tile, True)

    assert player.ai.current_strategy.type == BaseStrategy.YAKUHAI

    assert meld is not None


def chiitoitsu_tanyao_tempai():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="223344", pin="788", man="4577")
    player.init_hand(tiles)

    player.draw_tile(string_to_136_tile(man="4"))

    discard = player.discard_tile()
    discard_correct = tiles_to_string([discard]) == "7p" or tiles_to_string([discard]) == "5m"
    assert discard_correct is True
