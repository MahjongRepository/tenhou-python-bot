import pytest
from game.ai.helpers.defence import EnemyDanger
from game.table import Table
from utils.decisions_logger import MeldPrint
from utils.test_helpers import enemy_called_riichi_helper, make_meld, string_to_136_array, string_to_136_tile


def test_call_shouminkan_and_bad_ukeire_after_call():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="34445", sou="123456", pin="89")
    table.player.init_hand(tiles)
    tile = string_to_136_array(man="4444")[3]
    table.player.draw_tile(tile)

    assert table.player.should_call_kan(tile, False) is None

    table.player.add_called_meld(make_meld(MeldPrint.PON, man="444"))

    assert len(table.player.melds) == 1
    assert table.player.should_call_kan(tile, False) is None


def test_call_shouminkan_and_bad_ukeire_after_call_second_case():
    table = Table()
    table.add_dora_indicator(string_to_136_tile(honors="5"))
    table.count_of_remaining_tiles = 10
    player = table.player

    tiles = string_to_136_array(man="3455567", sou="222", honors="666")
    player.init_hand(tiles)
    player.add_called_meld(make_meld(MeldPrint.PON, man="555"))
    player.add_called_meld(make_meld(MeldPrint.PON, honors="666"))

    tile = string_to_136_array(man="5555")[3]
    player.draw_tile(tile)

    assert player.should_call_kan(tile, False) is None


def test_call_shouminkan_and_bad_ukeire_after_call_third_case():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="67", pin="6", sou="1344478999")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.PON, sou="444"))

    tile = string_to_136_array(sou="4444")[3]
    table.player.draw_tile(tile)

    # we don't want to call shouminkan here
    assert table.player.should_call_kan(tile, False) is None


def test_call_shouminkan():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="3455567", sou="222", honors="666")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.PON, honors="666"))

    tile = string_to_136_array(honors="6666")[3]
    table.player.draw_tile(tile)

    assert table.player.should_call_kan(tile, False) == MeldPrint.SHOUMINKAN


def test_shouminkan_and_weak_hand():
    table = Table()
    table.count_of_remaining_tiles = 40

    tiles = string_to_136_array(man="135567", sou="248", pin="5", honors="666")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.PON, honors="666"))

    tile = string_to_136_array(honors="6666")[3]
    table.player.draw_tile(tile)

    assert table.player.should_call_kan(tile, False) is None


def test_shouminkan_and_threatening_riichi():
    table = Table()
    table.count_of_remaining_tiles = 40

    enemy_seat = 2
    table.add_called_riichi_step_one(enemy_seat)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_RIICHI["id"]

    tiles = string_to_136_array(man="135567", sou="234", pin="5", honors="666")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.PON, honors="666"))

    tile = string_to_136_array(honors="6666")[3]
    table.player.draw_tile(tile)

    assert table.player.should_call_kan(tile, False) is None


def test_call_closed_kan():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="12223", sou="111456", pin="12")
    table.player.init_hand(tiles)
    tile = string_to_136_tile(man="2")
    table.player.draw_tile(tile)

    # it is pretty stupid to call closed kan with 2m
    assert table.player.should_call_kan(tile, False) is None

    tiles = string_to_136_array(man="12223", sou="111456", pin="12")
    table.player.init_hand(tiles)
    tile = string_to_136_tile(sou="1")
    table.player.draw_tile(tile)

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


def test_opened_kan_and_threatening_riichi():
    table = Table()
    table.count_of_remaining_tiles = 10

    enemy_seat = 2
    enemy_called_riichi_helper(table, enemy_seat)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_RIICHI["id"]

    tiles = string_to_136_array(man="2399", sou="111456", honors="111")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.PON, honors="111"))

    # to rebuild all caches
    table.player.draw_tile(string_to_136_tile(pin="9"))
    table.player.discard_tile()

    # our hand is open, in tempai and with a good wait but there is a riichi so calling open kan is a bad idea
    tile = string_to_136_tile(sou="1")
    assert table.player.should_call_kan(tile, True) is None
    assert table.player.try_to_call_meld(tile, True) == (None, None)


def test_closed_kan_and_wrong_shanten_number_calculation():
    """
    Bot tried to call riichi with 567m666p14578s + [9999s] hand
    """
    table = Table()
    player = table.player

    tiles = string_to_136_array(man="56", sou="145789999", pin="666")
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
    player.draw_tile(tile)

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
    player.draw_tile(tile)

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
    player.draw_tile(tile)

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
    table.player.draw_tile(tile)

    assert table.player.should_call_kan(tile, False) is None


def test_closed_kan_in_riichi():
    table = Table()
    table.count_of_remaining_tiles = 10

    tiles = string_to_136_array(man="456", pin="78999", sou="666", honors="33")
    table.player.init_hand(tiles)

    # to rebuild all caches
    table.player.draw_tile(string_to_136_tile(honors="6"))
    table.player.discard_tile()

    tile = string_to_136_tile(sou="6")
    table.player.draw_tile(tile)
    assert table.player.should_call_kan(tile, open_kan=False, from_riichi=True) == MeldPrint.KAN


@pytest.mark.skip("We need to be able properly handle old waiting and new waiting calculations")
def test_closed_kan_in_riichi_and_kan_that_breaking_hand_structure():
    table = Table()
    table.count_of_remaining_tiles = 10
    table.add_discarded_tile(1, string_to_136_tile(man="2"), True)
    table.add_discarded_tile(1, string_to_136_tile(man="2"), True)
    table.add_discarded_tile(1, string_to_136_tile(man="2"), True)
    table.add_discarded_tile(1, string_to_136_tile(man="2"), True)

    # 1113м456п234567с
    tiles = string_to_136_array(man="1113", pin="456", sou="234567")
    table.player.init_hand(tiles)

    # to rebuild all caches
    table.player.draw_tile(string_to_136_tile(honors="6"))
    table.player.discard_tile()

    tile = string_to_136_tile(man="1")
    table.player.draw_tile(tile)
    assert table.player.should_call_kan(tile, open_kan=False, from_riichi=True) is None
