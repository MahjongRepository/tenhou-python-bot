from game.ai.strategies.main import BaseStrategy
from game.table import Table
from mahjong.tile import TilesConverter
from utils.decisions_logger import MeldPrint
from utils.general import is_dora_connector
from utils.test_helpers import make_meld, string_to_34_tile, string_to_136_array, string_to_136_tile, tiles_to_string


def test_set_is_tempai_flag_to_the_player():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="111345677", pin="45", man="56")
    tile = string_to_136_array(man="9")[0]
    player.init_hand(tiles)
    player.draw_tile(tile)
    player.discard_tile()

    assert player.in_tempai is False

    tiles = string_to_136_array(sou="11145677", pin="345", man="56")
    tile = string_to_136_array(man="9")[0]
    player.init_hand(tiles)
    player.draw_tile(tile)
    player.discard_tile()

    assert player.in_tempai is True


def test_not_open_hand_in_riichi():
    table = Table()
    player = table.player

    player.in_riichi = True

    tiles = string_to_136_array(sou="12368", pin="2358", honors="4455")
    tile = string_to_136_tile(honors="5")
    player.init_hand(tiles)
    meld, _ = player.try_to_call_meld(tile, False)
    assert meld is None


def test_crash_when_tyring_to_open_meld():
    """
    Bot crashed when tried to calculate meld possibility with hand 7m333789s + 3s [222z, 123p]
    This test is checking that there are no crashes in such situations anymore
    """
    # checking a few similar hands here
    # #1
    table = Table()
    # dora here to activate honitsu strategy
    table.add_dora_indicator(string_to_136_tile(sou="9"))
    player = table.player

    tiles = string_to_136_array(sou="1112345678", honors="447")
    player.init_hand(tiles)
    tile = string_to_136_array(sou="1111")[3]
    meld, _ = player.try_to_call_meld(tile, False)
    assert meld is not None

    # #2
    table = Table()
    # dora here to activate honitsu strategy
    table.add_dora_indicator(string_to_136_tile(sou="9"))
    player = table.player

    tiles = string_to_136_array(sou="11123456789", honors="47")
    player.init_hand(tiles)
    tile = string_to_136_array(sou="1111")[3]
    meld, _ = player.try_to_call_meld(tile, False)
    assert meld is not None

    # #3
    table = Table()
    # dora here to activate honitsu strategy
    table.add_dora_indicator(string_to_136_tile(sou="9"))
    player = table.player

    tiles = string_to_136_array(sou="111234567", honors="4444")
    player.init_hand(tiles)
    table.add_called_meld(player.seat, make_meld(MeldPrint.PON, honors="444"))
    tile = string_to_136_array(sou="1111")[3]
    meld, _ = player.try_to_call_meld(tile, False)
    assert meld is not None

    # #4 - the original one
    table = Table()
    # dora here to activate yakuhai strategy
    table.add_dora_indicator(string_to_136_tile(sou="2"))
    player = table.player

    tiles = string_to_136_array(man="7", pin="123", sou="333789", honors="111")
    player.init_hand(tiles)
    table.add_called_meld(player.seat, make_meld(MeldPrint.PON, honors="111"))
    table.add_called_meld(player.seat, make_meld(MeldPrint.CHI, pin="123"))
    # it is important for crash to take fourth 3s (with index 83)
    tile = string_to_136_array(sou="3333")[3]
    meld, _ = player.try_to_call_meld(tile, False)
    assert meld is None


def test_crash_when_tyring_to_discard_with_open_hand():
    """
    Bot crashed when tried to discard tile from hand 266m4444z + 1z [111z, 789m]
    This test is checking that there are no crashes in such situations anymore
    """
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="266789", honors="1114444")
    player.init_hand(tiles)
    # we manually reveal one tile to emulate the fact that we saw it when it was discarded
    table._add_revealed_tile(string_to_136_tile(honors="1"))
    table.add_called_meld(player.seat, make_meld(MeldPrint.PON, honors="111"))
    table.add_called_meld(player.seat, make_meld(MeldPrint.CHI, man="789"))
    # it is important for crash to take fourth 4z
    tile = string_to_136_array(honors="1111")[3]
    player.draw_tile(tile)
    discard = player.discard_tile()
    assert discard is not None


def test_chose_right_set_to_open_hand():
    """
    Different test cases to open hand and chose correct set to open hand.
    Based on real examples of incorrect opened hands
    """
    table = Table()
    table.has_open_tanyao = True
    player = table.player

    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    table.add_dora_indicator(string_to_136_tile(pin="3"))

    tiles = string_to_136_array(man="23455", pin="3445678", honors="1")
    tile = string_to_136_array(man="5555")[2]
    player.init_hand(tiles)

    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.PON
    assert tiles_to_string(meld.tiles) == "555m"

    table = Table()
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="5"))
    tiles = string_to_136_array(man="335666", pin="22", sou="345", honors="55")
    player.init_hand(tiles)

    tile = string_to_136_tile(man="4")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "345m"

    table = Table()
    table.has_open_tanyao = True
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="1"))
    table.add_dora_indicator(string_to_136_tile(man="4"))
    tiles = string_to_136_array(man="23557", pin="556788", honors="22")
    player.init_hand(tiles)

    tile = string_to_136_array(pin="5555")[2]
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.PON
    assert tiles_to_string(meld.tiles) == "555p"

    table = Table()
    table.has_open_tanyao = True
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="4"))
    table.add_dora_indicator(string_to_136_tile(pin="5"))
    tiles = string_to_136_array(man="35568", pin="234668", sou="28")
    player.init_hand(tiles)

    tile = string_to_136_tile(man="4")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "345m"

    table = Table()
    table.has_open_tanyao = True
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="4"))
    table.add_dora_indicator(string_to_136_tile(pin="5"))
    tiles = string_to_136_array(man="34458", pin="234668", sou="28")
    player.init_hand(tiles)

    tile = string_to_136_array(man="4444")[2]
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "345m"

    table = Table()
    table.has_open_tanyao = True
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="7"))
    tiles = string_to_136_array(man="567888", pin="788", sou="3456")
    player.init_hand(tiles)

    tile = string_to_136_array(sou="4444")[1]
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "456s"

    tile = string_to_136_array(sou="5555")[1]
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "345s"

    table = Table()
    table.has_open_tanyao = True
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="7"))
    tiles = string_to_136_array(man="567888", pin="788", sou="2345")
    player.init_hand(tiles)

    tile = string_to_136_array(sou="4444")[1]
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "234s"


def test_chose_right_set_to_open_hand_dora():
    table = Table()
    table.has_open_tanyao = True
    table.has_aka_dora = False
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="7"))
    table.add_dora_indicator(string_to_136_tile(sou="1"))
    tiles = string_to_136_array(man="3456788", sou="245888")
    player.init_hand(tiles)

    tile = string_to_136_tile(sou="3")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "234s"

    table = Table()
    table.has_open_tanyao = True
    table.has_aka_dora = False
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="7"))
    table.add_dora_indicator(string_to_136_tile(sou="4"))
    tiles = string_to_136_array(man="3456788", sou="245888")
    player.init_hand(tiles)

    tile = string_to_136_tile(sou="3")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "345s"

    table = Table()
    table.has_open_tanyao = True
    table.has_aka_dora = True
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="7"))
    # 5 from string is always aka
    tiles = string_to_136_array(man="3456788", sou="240888")
    player.init_hand(tiles)

    tile = string_to_136_tile(sou="3")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "340s"

    table = Table()
    table.has_open_tanyao = True
    table.has_aka_dora = True
    player = table.player
    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="7"))
    table.add_dora_indicator(string_to_136_tile(sou="1"))
    table.add_dora_indicator(string_to_136_tile(sou="4"))
    # double dora versus regular dora, we should keep double dora
    tiles = string_to_136_array(man="3456788", sou="245888")
    player.init_hand(tiles)

    tile = string_to_136_tile(sou="3")
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert meld.type == MeldPrint.CHI
    assert tiles_to_string(meld.tiles) == "345s"


def test_not_open_hand_for_not_needed_set():
    """
    We don't need to open hand if it is not improve the hand.
    There was a bug related to it.
    """
    table = Table()
    player = table.player

    table.dora_indicators.append(string_to_136_tile(honors="7"))
    tiles = string_to_136_array(man="22457", sou="12234", pin="9", honors="55")
    player.init_hand(tiles)

    tile = string_to_136_array(sou="3333")[1]
    meld, discard_option = player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "123s"

    # fully update hand
    tiles = string_to_136_array(man="22457", sou="122334", pin="9", honors="55")
    player.init_hand(tiles)
    player.add_called_meld(meld)
    player.discard_tile(discard_option)

    tile = string_to_136_array(sou="3333")[2]
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is None


def test_chose_strategy_and_reset_strategy():
    table = Table()
    table.has_open_tanyao = True
    player = table.player

    # add 3 doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(man="2"))

    # we draw a tile that will set tanyao as our selected strategy
    tiles = string_to_136_array(man="33355788", sou="3479", honors="3")
    player.init_hand(tiles)

    tile = string_to_136_tile(sou="7")
    player.draw_tile(tile)
    assert player.ai.current_strategy is not None
    assert player.ai.current_strategy.type == BaseStrategy.TANYAO

    # we draw a tile that will change our selected strategy
    tiles = string_to_136_array(man="33355788", sou="3479", honors="3")
    player.init_hand(tiles)

    tile = string_to_136_tile(sou="2")
    meld, _ = player.try_to_call_meld(tile, False)
    assert player.ai.current_strategy is not None
    assert player.ai.current_strategy.type == BaseStrategy.TANYAO
    assert meld is None

    tile = string_to_136_tile(sou="8")
    player.draw_tile(tile)
    assert player.ai.current_strategy is None

    # for already opened hand we don't need to give up on selected strategy
    tiles = string_to_136_array(man="33355788", sou="3479", honors="3")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(honors="5"))
    player.discard_tile()

    meld = make_meld(MeldPrint.PON, man="333")
    player.add_called_meld(meld)
    tile = string_to_136_tile(sou="8")
    player.draw_tile(tile)

    assert player.ai.current_strategy is not None
    assert player.ai.current_strategy.type == BaseStrategy.TANYAO


def test_remaining_tiles_and_enemy_discard():
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="123456789", sou="167", honors="77")
    player.init_hand(tiles)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard_34 == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 8

    player.table.add_discarded_tile(1, string_to_136_tile(sou="5"), False)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard_34 == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 7

    player.table.add_discarded_tile(2, string_to_136_tile(sou="5"), False)
    player.table.add_discarded_tile(3, string_to_136_tile(sou="8"), False)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard_34 == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 5


def test_remaining_tiles_and_opened_meld():
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="123456789", sou="167", honors="77")
    player.init_hand(tiles)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard_34 == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 8

    # was discard and set was opened
    tile = string_to_136_tile(sou="8")
    player.table.add_discarded_tile(3, tile, False)
    meld = make_meld(MeldPrint.PON, sou="888")
    meld.called_tile = tile
    player.table.add_called_meld(3, meld)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard_34 == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 5

    # was discard and set was opened
    tile = string_to_136_tile(sou="3")
    player.table.add_discarded_tile(2, tile, False)
    meld = make_meld(MeldPrint.PON, sou="345")
    meld.called_tile = tile
    player.table.add_called_meld(2, meld)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard_34 == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 4


def test_remaining_tiles_and_dora_indicators():
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="123456789", sou="167", honors="77")
    player.init_hand(tiles)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard_34 == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 8

    table.add_dora_indicator(string_to_136_tile(sou="8"))

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard_34 == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 7


def test_using_tiles_of_different_suit_for_chi():
    """
    It was a bug related to it, when bot wanted to call 9p12s chi :(
    """
    table = Table()
    player = table.player

    # 16m2679p1348s111z
    table.dora_indicators.append(string_to_136_tile(honors="4"))
    tiles = [0, 21, 41, 56, 61, 70, 74, 80, 84, 102, 108, 110, 111]
    player.init_hand(tiles)

    # 2s
    tile = 77
    meld, _ = player.try_to_call_meld(tile, True)
    assert meld is not None


def test_shanten_and_hand_structure():
    table = Table()
    player = table.player

    table.add_dora_indicator(string_to_136_tile(man="2"))

    tiles = string_to_136_array(man="33344455", pin="34567")
    player.init_hand(tiles)
    player.melds.append(make_meld(MeldPrint.CHI, man="345"))
    player.melds.append(make_meld(MeldPrint.CHI, man="345"))

    closed_hand_34 = TilesConverter.to_34_array(player.closed_hand)

    shanten, _ = player.ai.hand_builder.calculate_shanten_and_decide_hand_structure(closed_hand_34)
    assert shanten == 1


def test_is_dora_connector():
    cases = [
        {
            "dora_indicators": [string_to_136_tile(sou="5")],
            "dora_connectors": [string_to_136_tile(sou="4"), string_to_136_tile(sou="6")],
        },
        {
            "dora_indicators": [string_to_136_tile(sou="5"), string_to_136_tile(sou="4")],
            "dora_connectors": [
                string_to_136_tile(sou="3"),
                string_to_136_tile(sou="4"),
                string_to_136_tile(sou="5"),
                string_to_136_tile(sou="6"),
            ],
        },
        {
            "dora_indicators": [string_to_136_tile(pin="1")],
            "dora_connectors": [
                string_to_136_tile(pin="2"),
            ],
        },
        {
            "dora_indicators": [string_to_136_tile(man="9")],
            "dora_connectors": [
                string_to_136_tile(man="8"),
            ],
        },
        {
            "dora_indicators": [string_to_136_tile(honors="1")],
            "dora_connectors": [],
        },
    ]

    for case in cases:
        dora_connectors_34 = [x // 4 for x in case["dora_connectors"]]
        for tile_34 in range(0, 34):
            if tile_34 in dora_connectors_34:
                assert is_dora_connector(tile_34 * 4, case["dora_indicators"]) is True
            else:
                assert is_dora_connector(tile_34 * 4, case["dora_indicators"]) is False
