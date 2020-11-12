import pytest
from game.ai.strategies.main import BaseStrategy
from game.table import Table
from mahjong.tile import TilesConverter
from utils.decisions_logger import MeldPrint
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


@pytest.mark.skip("Skipped while debugging it further, ref #147")
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


@pytest.mark.skip("Skipped while debugging it further, ref #148")
def test_crash_when_tyring_to_discard_with_open_hand():
    """
    Bot crashed when tried to discard tile from hand 266m4444z + 1z [111z, 789m]
    This test is checking that there are no crashes in such situations anymore
    """
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="266789", honors="1114444")
    player.init_hand(tiles)
    player.add_called_meld(make_meld(MeldPrint.PON, honors="111"))
    player.add_called_meld(make_meld(MeldPrint.CHI, man="789"))
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
    result = [x for x in results if x.tile_to_discard == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 8

    player.table.add_discarded_tile(1, string_to_136_tile(sou="5"), False)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 7

    player.table.add_discarded_tile(2, string_to_136_tile(sou="5"), False)
    player.table.add_discarded_tile(3, string_to_136_tile(sou="8"), False)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 5


def test_remaining_tiles_and_opened_meld():
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="123456789", sou="167", honors="77")
    player.init_hand(tiles)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 8

    # was discard and set was opened
    tile = string_to_136_tile(sou="8")
    player.table.add_discarded_tile(3, tile, False)
    meld = make_meld(MeldPrint.PON, sou="888")
    meld.called_tile = tile
    player.table.add_called_meld(3, meld)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 5

    # was discard and set was opened
    tile = string_to_136_tile(sou="3")
    player.table.add_discarded_tile(2, tile, False)
    meld = make_meld(MeldPrint.PON, sou="345")
    meld.called_tile = tile
    player.table.add_called_meld(2, meld)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 4


def test_remaining_tiles_and_dora_indicators():
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="123456789", sou="167", honors="77")
    player.init_hand(tiles)

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard == string_to_34_tile(sou="1")][0]
    assert result.ukeire == 8

    table.add_dora_indicator(string_to_136_tile(sou="8"))

    results, shanten = player.ai.hand_builder.find_discard_options()
    result = [x for x in results if x.tile_to_discard == string_to_34_tile(sou="1")][0]
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


def test_call_upgrade_pon_and_bad_ukeire_after_call():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="34445", sou="123456", pin="89")
    table.player.init_hand(tiles)
    tile = string_to_136_array(man="4444")[3]

    assert table.player.should_call_kan(tile, False) is None

    table.player.add_called_meld(make_meld(MeldPrint.PON, man="444"))

    assert len(table.player.melds) == 1
    assert len(table.player.tiles) == 13
    assert table.player.should_call_kan(tile, False) is None


def test_call_upgrade_pon_and_bad_ukeire_after_call_second_case():
    table = Table()
    table.add_dora_indicator(string_to_136_tile(honors="5"))
    table.count_of_remaining_tiles = 10
    player = table.player

    tiles = string_to_136_array(man="3455567", sou="222", honors="666")
    player.init_hand(tiles)
    player.add_called_meld(make_meld(MeldPrint.PON, man="555"))
    player.add_called_meld(make_meld(MeldPrint.PON, honors="666"))

    tile = string_to_136_array(man="5555")[3]

    assert player.should_call_kan(tile, False) is None


def test_call_upgrade_pon_and_bad_ukeire_after_call_third_case():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="67", pin="6", sou="1344478999")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.PON, sou="444"))

    tile = string_to_136_array(sou="4444")[3]

    # we don't want to call shouminkan here
    assert table.player.should_call_kan(tile, False) is None


def test_call_shouminkan():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="3455567", sou="222", honors="666")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.PON, honors="666"))

    tile = string_to_136_array(honors="6666")[3]

    assert table.player.should_call_kan(tile, False) == MeldPrint.SHOUMINKAN


def test_call_closed_kan():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="12223", sou="111456", pin="12")
    table.player.init_hand(tiles)
    tile = string_to_136_tile(man="2")

    # it is pretty stupid to call closed kan with 2m
    assert table.player.should_call_kan(tile, False) is None

    tiles = string_to_136_array(man="12223", sou="111456", pin="12")
    table.player.init_hand(tiles)
    tile = string_to_136_tile(sou="1")

    # call closed kan with 1s is fine
    assert table.player.should_call_kan(tile, False) == MeldPrint.KAN


def test_opened_kan():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="299", sou="111456", pin="1", honors="111")
    table.player.init_hand(tiles)

    # to rebuild all caches
    table.player.draw_tile(string_to_136_tile(pin="9"))
    table.player.discard_tile()

    # our hand is closed, we don't need to call opened kan here
    tile = string_to_136_tile(sou="1")
    assert table.player.should_call_kan(tile, True) is None

    table.player.add_called_meld(make_meld(MeldPrint.PON, honors="111"))

    # our hand is open, but it is not tempai
    # we don't need to open kan here
    tile = string_to_136_tile(sou="1")
    assert table.player.should_call_kan(tile, True) is None


def test_opened_kan_second_case():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="2399", sou="111456", honors="111")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.PON, honors="111"))

    # to rebuild all caches
    table.player.draw_tile(string_to_136_tile(pin="9"))
    table.player.discard_tile()

    # our hand is open, in tempai and with a good wait
    tile = string_to_136_tile(sou="1")
    assert table.player.should_call_kan(tile, True) == MeldPrint.KAN


def test_opened_kan_third_case():
    # we are in tempai already and there was a crash on 5s meld suggestion

    table = Table()
    table.count_of_remaining_tiles = 10
    table.add_dora_indicator(string_to_136_tile(honors="5"))

    tiles = string_to_136_array(man="456", sou="55567678", honors="66")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, sou="678"))

    # to rebuild all caches
    table.player.draw_tile(string_to_136_tile(pin="9"))
    table.player.discard_tile()

    tile = string_to_136_array(sou="5555")[3]
    assert table.player.should_call_kan(tile, True) is None
    assert table.player.try_to_call_meld(tile, True) == (None, None)


def test_closed_kan_and_wrong_shanten_number_calculation():
    """
    Bot tried to call riichi with 567m666p14578s + [9999s] hand
    """
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="56", sou="14578999", pin="666")
    player.init_hand(tiles)
    tile = string_to_136_tile(man="7")
    player.table.add_called_meld(player.seat, make_meld(MeldPrint.KAN, False, sou="9999"))
    # we have to do it manually in test
    # normally tenhou client would do that
    player.table._add_revealed_tile(string_to_136_tile(sou="9"))
    player.draw_tile(tile)
    player.discard_tile()

    # bot not in the tempai, because all 9s in the closed kan
    assert player.ai.shanten == 1


def test_closed_kan_and_not_necessary_call():
    """
    Bot tried to call closed kan with 568m669p1478999s + 9s hand
    """
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="568", sou="1478999", pin="669")
    player.init_hand(tiles)
    tile = string_to_136_tile(sou="9")

    assert player.should_call_kan(tile, False) is None


def test_closed_kan_same_shanten_bad_ukeire():
    """
    Bot tried to call closed kan with 4557888899m2z + 333m melded hand
    Shanten number is the same, but ukeire becomes much worse
    """
    table = Table()
    player = table.player

    table.add_dora_indicator(string_to_136_tile(honors="2"))
    table.add_dora_indicator(string_to_136_tile(honors="4"))

    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="333455788899", honors="3")
    player.init_hand(tiles)
    player.melds.append(make_meld(MeldPrint.PON, man="333"))

    tile = string_to_136_tile(man="8")

    assert player.should_call_kan(tile, False) is None


def test_closed_kan_same_shanten_same_ukeire():
    table = Table()
    player = table.player

    table.add_dora_indicator(string_to_136_tile(honors="2"))
    table.add_dora_indicator(string_to_136_tile(honors="4"))

    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="3334557889", honors="333")
    player.init_hand(tiles)
    player.melds.append(make_meld(MeldPrint.PON, man="333"))

    tile = string_to_136_tile(honors="3")

    assert player.should_call_kan(tile, False) == MeldPrint.KAN


def test_kan_crash():
    """
    This was a crash in real game
    related with open kan logic and agari without yaku state
    """
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="456", pin="78999", sou="666", honors="33")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.PON, sou="666"))
    tile = string_to_136_tile(pin="9")

    assert table.player.should_call_kan(tile, False) is None


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
