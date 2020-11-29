import pytest
from game.ai.strategies.main import BaseStrategy
from game.ai.strategies.yakuhai import YakuhaiStrategy
from game.table import Table
from mahjong.constants import EAST, SOUTH, WEST
from mahjong.tile import Tile
from utils.decisions_logger import MeldPrint
from utils.test_helpers import make_meld, string_to_136_array, string_to_136_tile, tiles_to_string


def test_should_activate_strategy():
    table = Table()
    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, table.player)

    tiles = string_to_136_array(sou="12355689", man="89", honors="123")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    table.dora_indicators.append(string_to_136_tile(honors="7"))
    tiles = string_to_136_array(sou="12355689", man="899", honors="55")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is True

    # with chitoitsu-like hand we don't need to go for yakuhai
    tiles = string_to_136_array(sou="1235566", man="8899", honors="66")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    # don't count tile discarded by other player as our pair
    tiles = string_to_136_array(sou="12355689", man="899", honors="25")
    table.player.init_hand(tiles)
    tiles = string_to_136_array(sou="12355689", man="899", honors="255")
    assert strategy.should_activate_strategy(tiles) is False


def test_dont_activate_strategy_if_we_dont_have_enough_tiles_in_the_wall():
    table = Table()
    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, table.player)

    table.dora_indicators.append(string_to_136_tile(honors="7"))
    tiles = string_to_136_array(man="59", sou="1235", pin="12789", honors="55")
    table.player.init_hand(tiles)

    assert strategy.should_activate_strategy(table.player.tiles) is True

    table.add_discarded_tile(3, string_to_136_tile(honors="5"), False)
    table.add_discarded_tile(3, string_to_136_tile(honors="5"), False)

    # we can't complete yakuhai, because there is not enough honor tiles
    assert strategy.should_activate_strategy(table.player.tiles) is False


def test_suitable_tiles():
    table = Table()
    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, table.player)

    # for yakuhai we can use any tile
    for tile in range(0, 136):
        assert strategy.is_tile_suitable(tile) is True


def test_force_yakuhai_pair_waiting_for_tempai_hand():
    """
    If hand shanten = 1 don't open hand except the situation where is
    we have tempai on yakuhai tile after open set
    """
    table = Table()

    table.dora_indicators.append(string_to_136_tile(man="3"))
    tiles = string_to_136_array(sou="123", pin="678", man="34468", honors="66")
    table.player.init_hand(tiles)

    # we will not get tempai on yakuhai pair with this hand, so let's skip this call
    tile = string_to_136_tile(man="5")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is None

    # but here we will have atodzuke tempai
    tile = string_to_136_tile(man="7")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "678m"

    table = Table()
    # we can open hand in that case
    table.dora_indicators.append(string_to_136_tile(sou="5"))
    tiles = string_to_136_array(man="44556", sou="366789", honors="77")
    table.player.init_hand(tiles)

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, table.player)
    assert strategy.should_activate_strategy(table.player.tiles) is True

    tile = string_to_136_tile(honors="7")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "777z"


def test_tempai_without_yaku():
    table = Table()
    tiles = string_to_136_array(sou="678", pin="12355", man="456", honors="77")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="5")
    table.player.draw_tile(tile)
    meld = make_meld(MeldPrint.CHI, sou="678")
    table.player.add_called_meld(meld)

    discard, _ = table.player.discard_tile()
    assert tiles_to_string([discard]) != "7z"


def test_wrong_shanten_improvements_detection():
    """
    With hand 2345s1p11z bot wanted to open set on 2s,
    so after opened set we will get 25s1p11z
    it is not correct logic, because we ruined our hand
    :return:
    """
    table = Table()

    tiles = string_to_136_array(sou="2345999", honors="114446")
    table.player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, sou="999")
    table.player.add_called_meld(meld)
    meld = make_meld(MeldPrint.PON, honors="444")
    table.player.add_called_meld(meld)

    tile = string_to_136_array(sou="2222")[1]
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_open_hand_with_doras_in_the_hand():
    """
    If we have valuable pair in the hand, and 2+ dora let's open on this
    valuable pair
    """
    table = Table()
    table.player.dealer_seat = 3

    tiles = string_to_136_array(man="59", sou="1235", pin="12789", honors="11")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(honors="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # add doras to the hand
    table.dora_indicators.append(string_to_136_tile(pin="7"))
    table.dora_indicators.append(string_to_136_tile(pin="8"))
    table.player.init_hand(tiles)

    # and now we can open hand on the valuable pair
    tile = string_to_136_tile(honors="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # but we don't need to open hand for atodzuke here
    tile = string_to_136_tile(pin="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_open_hand_with_doras_in_the_hand_and_atodzuke():
    """
    If we have valuable pair in the hand, and 2+ dora we can open hand on any tile
    but only if we have other pair in the hand
    """
    table = Table()
    table.player.dealer_seat = 3

    tiles = string_to_136_array(man="59", sou="1235", pin="12788", honors="11")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # add doras to the hand
    table.dora_indicators.append(string_to_136_tile(pin="7"))
    table.player.init_hand(tiles)

    # we have other pair in the hand, so we can open atodzuke here
    tile = string_to_136_tile(pin="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None


def test_open_hand_on_fifth_round_step():
    """
    If we have valuable pair in the hand, 1+ dora and 5+ round step
    let's open on this valuable pair
    """
    table = Table()
    table.player.dealer_seat = 3

    tiles = string_to_136_array(man="59", sou="1235", pin="12789", honors="11")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(honors="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # add doras to the hand
    table.dora_indicators.append(string_to_136_tile(pin="7"))
    table.player.init_hand(tiles)

    tile = string_to_136_tile(honors="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # one discard == one round step
    table.player.add_discarded_tile(Tile(0, False))
    table.player.add_discarded_tile(Tile(0, False))
    table.player.add_discarded_tile(Tile(0, False))
    table.player.add_discarded_tile(Tile(0, False))
    table.player.add_discarded_tile(Tile(0, False))
    table.player.add_discarded_tile(Tile(0, False))
    table.player.init_hand(tiles)

    # after 5 round step we can open hand
    tile = string_to_136_tile(honors="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # but we don't need to open hand for atodzuke here
    tile = string_to_136_tile(pin="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_open_hand_with_two_valuable_pairs():
    """
    If we have two valuable pairs in the hand and 1+ dora or we are dealer
    let's open on one of this valuable pairs
    """
    table = Table()
    table.player.seat = 3

    tiles = string_to_136_array(man="159", sou="128", pin="789", honors="5566")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(honors="5")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # add doras to the hand
    table.dora_indicators.append(string_to_136_tile(pin="7"))
    table.player.init_hand(tiles)

    tile = string_to_136_tile(honors="5")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    tile = string_to_136_tile(honors="6")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # but we don't need to open hand for atodzuke here
    tile = string_to_136_tile(pin="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_open_hand_and_once_discarded_tile():
    """
    If we have valuable pair in the hand, this tile was discarded once and we have 1+ shanten
    let's open on this valuable pair
    """
    table = Table()
    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, table.player)

    tiles = string_to_136_array(sou="678", pin="14689", man="456", honors="77")
    table.player.init_hand(tiles)

    # we don't activate strategy yet
    assert strategy.should_activate_strategy(table.player.tiles) is False

    # let's skip first yakuhai early in the game
    tile = string_to_136_tile(honors="7")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # now one is out
    table.add_discarded_tile(1, tile, False)

    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "777z"

    # but we don't need to open hand for atodzuke here
    tile = string_to_136_tile(pin="7")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_open_hand_when_yakuhai_already_in_the_hand():
    # make sure yakuhai strategy is activated by adding 3 doras to the hand
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(honors="5"))

    tiles = string_to_136_array(man="46", pin="4679", sou="1348", honors="666")
    player.init_hand(tiles)

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    tile = string_to_136_tile(sou="2")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None


def test_always_open_double_east_wind():
    table = Table()
    tiles = string_to_136_array(man="59", sou="1235", pin="12788", honors="11")
    table.player.init_hand(tiles)

    # player is is not east
    table.player.dealer_seat = 2
    assert table.player.player_wind == WEST

    table.player.init_hand(tiles)
    tile = string_to_136_tile(honors="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # player is is east
    table.player.dealer_seat = 0
    assert table.player.player_wind == EAST

    table.player.init_hand(tiles)
    tile = string_to_136_tile(honors="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None


def test_open_double_south_wind():
    table = Table()
    tiles = string_to_136_array(man="59", sou="1235", pin="12788", honors="22")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(honors="2")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # player is south and round is south
    table.round_wind_number = 5
    table.player.dealer_seat = 3
    assert table.player.player_wind == SOUTH

    table.player.init_hand(tiles)
    tile = string_to_136_tile(honors="2")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # add dora in the hand and after that we can open a hand
    table.dora_indicators.append(string_to_136_tile(pin="6"))

    table.player.init_hand(tiles)
    tile = string_to_136_tile(honors="2")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None


def test_keep_yakuhai_in_closed_hand():
    table = Table()
    tiles = string_to_136_array(man="14", sou="15", pin="113347", honors="777")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(honors="3")
    table.player.draw_tile(tile)

    discard, _ = table.player.discard_tile()
    assert tiles_to_string([discard]) != "7z"


def test_keep_only_yakuhai_pon():
    # make sure yakuhai strategy is activated by adding 3 doras to the hand
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(man="9"))
    table.add_dora_indicator(string_to_136_tile(man="3"))

    tiles = string_to_136_array(man="11144", sou="567", pin="56", honors="777")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, man="111")
    player.add_called_meld(meld)

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    player.draw_tile(string_to_136_tile(man="4"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) != "7z"


def test_keep_only_yakuhai_pair():
    # make sure yakuhai strategy is activated by adding 3 doras to the hand
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(man="9"))
    table.add_dora_indicator(string_to_136_tile(man="3"))

    table.add_discarded_tile(1, string_to_136_tile(honors="7"), False)

    tiles = string_to_136_array(man="11144", sou="567", pin="156", honors="77")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, man="111")
    player.add_called_meld(meld)

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    player.draw_tile(string_to_136_tile(pin="1"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) != "7z"


def test_atodzuke_keep_yakuhai_wait():
    # make sure yakuhai strategy is activated by adding 3 doras to the hand
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(man="9"))

    tiles = string_to_136_array(man="11144", sou="567", pin="567", honors="77")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, man="111")
    player.add_called_meld(meld)

    # two of 4 man tiles are already out, so it would seem our wait is worse, but we know
    # we must keep two pairs in order to be atodzuke tempai
    table.add_discarded_tile(1, string_to_136_tile(man="4"), False)
    table.add_discarded_tile(1, string_to_136_tile(man="4"), False)

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    player.draw_tile(string_to_136_tile(man="2"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "2m"


@pytest.mark.skip("Need to implement logic for these tests. Github issue #98")
def test_atodzuke_dont_destroy_second_pair():
    # make sure yakuhai strategy is activated by adding 3 doras to the hand
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(man="9"))

    tiles = string_to_136_array(man="111445", sou="468", pin="56", honors="77")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, man="111")
    player.add_called_meld(meld)

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    # 6 man is bad meld, we lose our second pair and so is 4 man
    tile = string_to_136_tile(man="6")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is None

    tile = string_to_136_tile(man="4")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is None

    # but if we have backup pair it's ok
    tiles = string_to_136_array(man="111445", sou="468", pin="88", honors="77")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, man="111")
    player.add_called_meld(meld)

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    # 6 man is bad meld, we lose our second pair and so is 4 man
    tile = string_to_136_tile(man="6")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None

    tile = string_to_136_tile(man="4")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None


def test_atodzuke_dont_open_no_yaku_tempai():
    # make sure yakuhai strategy is activated by adding 3 doras to the hand
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(man="9"))

    tiles = string_to_136_array(man="111445", sou="567", pin="56", honors="77")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, man="111")
    player.add_called_meld(meld)

    # 6 man is bad meld, we lose our second pair and so is 4 man
    tile = string_to_136_tile(man="6")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is None

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    tile = string_to_136_tile(man="4")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is None

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    # 7 pin is a good meld, we get to tempai keeping yakuhai wait
    tile = string_to_136_tile(pin="7")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True


def test_atodzuke_choose_hidden_syanpon():
    # make sure yakuhai strategy is activated by adding 3 doras to the hand
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(man="9"))

    tiles = string_to_136_array(man="111678", sou="56678", honors="77")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, man="111")
    player.add_called_meld(meld)

    strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)
    assert strategy.should_activate_strategy(player.tiles) is True

    for _ in range(0, 4):
        table.add_discarded_tile(1, string_to_136_tile(sou="9"), False)

    player.draw_tile(string_to_136_tile(sou="6"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) != "6s"
    assert tiles_to_string([discarded_tile]) == "5s" or tiles_to_string([discarded_tile]) == "8s"


def test_tempai_with_open_yakuhai_meld_and_yakuhai_pair_in_the_hand():
    """
    there was a bug where bot didn't handle tempai properly
    with opened yakuhai pon and pair in the hand
    56m555p6678s55z + [777z]
    """
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="56", pin="555", sou="667", honors="55777")
    player.init_hand(tiles)
    player.add_called_meld(make_meld(MeldPrint.PON, honors="777"))
    player.draw_tile(string_to_136_tile(sou="8"))

    player.ai.current_strategy = YakuhaiStrategy(BaseStrategy.YAKUHAI, player)

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "6s"


def test_tempai_with_closed_kan():
    """
    there was a bug where bot didn't handle tempai properly
    with closed kan which was viewed as open one and thus open hand
    """
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="56", pin="4444", sou="223789", honors="55")
    player.init_hand(tiles)
    player.table.add_called_meld(player.seat, make_meld(MeldPrint.KAN, False, pin="4444"))
    player.draw_tile(string_to_136_tile(sou="1"))

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "2s"
