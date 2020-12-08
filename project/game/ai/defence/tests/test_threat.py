from game.ai.defence.yaku_analyzer.chinitsu import ChinitsuAnalyzer
from game.ai.defence.yaku_analyzer.honitsu import HonitsuAnalyzer
from game.ai.helpers.defence import EnemyDanger
from game.table import Table
from mahjong.utils import is_honor
from utils.decisions_logger import MeldPrint
from utils.test_helpers import (
    enemy_called_riichi_helper,
    make_meld,
    string_to_34_tile,
    string_to_136_array,
    string_to_136_tile,
)


def test_is_threatening_and_riichi():
    table = Table()

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 2
    enemy_called_riichi_helper(table, enemy_seat)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_RIICHI["id"]


def test_is_threatening_and_dora_pon():
    table = Table()

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 2
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, man="333"))
    table.player.round_step = 7

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="7"), False)

    # simple pon it is no threat
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    # dora pon is threat
    table.add_dora_indicator(string_to_136_tile(man="2"))
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_OPEN_HAND_AND_MULTIPLE_DORA["id"]
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(man="2")) == 8000


def test_is_threatening_and_two_open_yakuhai_melds():
    table = Table()

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    # south player
    enemy_seat = 1
    # south round
    table.round_wind_number = 4

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, honors="222"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, man="123"))
    table.player.round_step = 2

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="3"), False)

    # double wind is not enough
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    # with one dora in enemy melds we can start think about threat
    # it will be 3 han
    table.add_dora_indicator(string_to_136_tile(man="1"))
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND["id"]
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(man="8")) == 3900

    for tile_136 in range(0, 136):
        bonus_danger = threatening_players[0].threat_reason.get("active_yaku")[0].get_bonus_danger(tile_136, 1)
        assert not bonus_danger


def test_is_threatening_and_two_open_tanyao_melds():
    table = Table()

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 2
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, pin="234"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, sou="333"))
    table.player.round_step = 2

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="3"), False)

    # tanyao without doras is not threat
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    # and now it is threat
    table.add_dora_indicator(string_to_136_tile(pin="1"))
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND["id"]
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(man="2")) == 3900

    for tile_136 in range(0, 136):
        bonus_danger = threatening_players[0].threat_reason.get("active_yaku")[0].get_bonus_danger(tile_136, 1)
        assert not bonus_danger


def test_is_threatening_and_honitsu_hand():
    table = Table()
    table.add_dora_indicator(string_to_136_tile(pin="1"))

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 1
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, honors="444"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, pin="123"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, pin="345"))

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), False)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND["id"]
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(pin="4")) == 3900
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(pin="2")) == 8000
    assert HonitsuAnalyzer.id in [x.id for x in threatening_players[0].threat_reason["active_yaku"]]

    honitsu_analyzer = [x for x in threatening_players[0].threat_reason["active_yaku"] if x.id == HonitsuAnalyzer.id][0]

    for tile_136 in range(0, 136):
        bonus_danger = honitsu_analyzer.get_bonus_danger(tile_136, 1)
        if is_honor(tile_136 // 4):
            assert bonus_danger
        else:
            assert not bonus_danger


def test_is_threatening_and_chinitsu_hand():
    table = Table()
    table.add_dora_indicator(string_to_136_tile(pin="1"))

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 1
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, pin="666"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, pin="123"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, pin="234"))

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), False)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND["id"]
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(pin="4")) == 12000
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(pin="2")) == 16000
    assert ChinitsuAnalyzer.id in [x.id for x in threatening_players[0].threat_reason["active_yaku"]]

    chinitsu_analyzer = [x for x in threatening_players[0].threat_reason["active_yaku"] if x.id == ChinitsuAnalyzer.id][
        0
    ]

    for tile_136 in range(0, 136):
        bonus_danger = chinitsu_analyzer.get_bonus_danger(tile_136, 1)
        assert not bonus_danger


def test_is_threatening_and_toitoi_melds():
    table = Table()

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 2
    table.player.round_step = 2
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, pin="222"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, honors="444"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, sou="999"))

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="3"), False)

    table.add_dora_indicator(string_to_136_tile(pin="1"))

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND["id"]
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(man="2")) == 8000


def test_threatening_riichi_player_and_default_hand_cost():
    table = Table()
    enemy_seat = 2
    enemy_called_riichi_helper(table, enemy_seat)

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 2000

    # dealer
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 2900


def test_threatening_riichi_player_and_not_early_hand_bonus():
    table = Table()
    enemy_seat = 2
    discards = string_to_136_array(sou="111122")
    for discard in discards:
        table.add_discarded_tile(enemy_seat, discard, False)
    enemy_called_riichi_helper(table, enemy_seat)

    # +1 scale for riichi on 6+ turn
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 3900


def test_threatening_riichi_player_middle_tiles_bonus():
    table = Table()
    enemy_seat = 2
    enemy_called_riichi_helper(table, enemy_seat)

    # +1 scale 456 tiles
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat

    # +1 scale 456 tiles
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="4"), can_be_used_for_ryanmen=True) == 3900
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="5"), can_be_used_for_ryanmen=True) == 3900
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="6"), can_be_used_for_ryanmen=True) == 3900
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="5"), can_be_used_for_ryanmen=False) == 3900

    # +1 scare for 2378 tiles that could be used in ryanmen
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(pin="2"), can_be_used_for_ryanmen=True) == 3900
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(pin="2"), can_be_used_for_ryanmen=False) == 2000
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(sou="7"), can_be_used_for_ryanmen=True) == 3900
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(sou="7"), can_be_used_for_ryanmen=False) == 2000

    # not middle tiles
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="1"), can_be_used_for_ryanmen=True) == 2000
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(pin="9"), can_be_used_for_ryanmen=True) == 2000


def test_threatening_riichi_player_and_not_visible_dora():
    table = Table()
    enemy_seat = 2
    table.add_dora_indicator(string_to_136_tile(sou="2"))

    discards = string_to_136_array(sou="3333222")
    for discard in discards:
        table.add_discarded_tile(enemy_seat, discard, False)

    enemy_called_riichi_helper(table, enemy_seat)

    # +1 scale for riichi on 6+ turn
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 3900
    # on dora discard, enemy hand will be on average more expensive
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(sou="3")) == 5200


def test_threatening_riichi_player_with_kan():
    table = Table()
    enemy_seat = 2
    enemy_called_riichi_helper(table, enemy_seat)

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, man="3333"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 5200

    # dealer
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 7700


def test_threatening_riichi_player_with_kan_aka():
    table = Table()
    enemy_seat = 2
    enemy_called_riichi_helper(table, enemy_seat)
    table.has_aka_dora = True

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, man="5505"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(sou="2")) == 8000

    # dealer
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(sou="2")) == 12000


def test_threatening_riichi_player_with_dora_kan():
    table = Table()
    enemy_seat = 2
    enemy_called_riichi_helper(table, enemy_seat)

    table.add_dora_indicator(string_to_136_tile(man="2"))

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, man="3333"))
    # we have to do it manually in test
    # normally tenhou client would do that
    table._add_revealed_tile(string_to_136_tile(man="3"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 12000

    # dealer
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 18000


def test_threatening_riichi_player_with_yakuhai_kan():
    table = Table()
    enemy_seat = 2
    table.round_wind_number = 1
    enemy_called_riichi_helper(table, enemy_seat)

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, honors="1111"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 8000


def test_threatening_riichi_player_with_double_yakuhai_kan():
    table = Table()
    enemy_seat = 2
    table.round_wind_number = 1
    enemy_called_riichi_helper(table, enemy_seat)

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, honors="1111"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.get_assumed_hand_cost(string_to_136_tile(man="2")) == 12000


def test_number_of_unverified_suji():
    table = Table()
    enemy_seat = 2
    enemy_called_riichi_helper(table, enemy_seat)

    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.number_of_unverified_suji == 18

    table.add_discarded_tile(0, string_to_136_tile(sou="4"), True)
    assert threatening_player.number_of_unverified_suji == 16
    table.add_discarded_tile(0, string_to_136_tile(sou="1"), True)
    table.add_discarded_tile(0, string_to_136_tile(sou="7"), True)
    assert threatening_player.number_of_unverified_suji == 16

    table.add_discarded_tile(0, string_to_136_tile(sou="2"), True)
    assert threatening_player.number_of_unverified_suji == 15
    table.add_discarded_tile(0, string_to_136_tile(sou="8"), True)
    assert threatening_player.number_of_unverified_suji == 14
    table.add_discarded_tile(0, string_to_136_tile(sou="5"), True)
    assert threatening_player.number_of_unverified_suji == 14

    table.add_discarded_tile(0, string_to_136_tile(sou="6"), True)
    assert threatening_player.number_of_unverified_suji == 12
    table.add_discarded_tile(0, string_to_136_tile(man="4"), True)
    table.add_discarded_tile(0, string_to_136_tile(man="5"), True)
    table.add_discarded_tile(0, string_to_136_tile(man="6"), True)
    assert threatening_player.number_of_unverified_suji == 6

    table.add_discarded_tile(0, string_to_136_tile(pin="1"), True)
    table.add_discarded_tile(0, string_to_136_tile(pin="7"), True)
    assert threatening_player.number_of_unverified_suji == 4
    table.add_discarded_tile(0, string_to_136_tile(pin="5"), True)
    assert threatening_player.number_of_unverified_suji == 2
    table.add_discarded_tile(0, string_to_136_tile(pin="6"), True)
    assert threatening_player.number_of_unverified_suji == 0


def test_is_threatening_and_atodzuke():
    table = Table()

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    table.add_dora_indicator(string_to_136_tile(honors="5"))

    enemy_seat = 2
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.CHI, man="234"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, sou="333"))
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, pin="9999"))
    table.player.round_step = 5

    table.add_discarded_tile(enemy_seat, string_to_136_tile(honors="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(honors="4"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="6"), False)

    # atodzuke with 3 melds is a threat
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_OPEN_HAND_UNKNOWN_COST["id"]
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(honors="5")) == 2000
    assert threatening_players[0].get_assumed_hand_cost(string_to_136_tile(honors="6")) == 8000

    for tile_136 in range(0, 136):
        bonus_danger = threatening_players[0].threat_reason.get("active_yaku")[0].get_bonus_danger(tile_136, 1)
        if not is_honor(tile_136 // 4):
            assert not bonus_danger
        elif (
            (tile_136 // 4 == string_to_34_tile(honors="1"))
            or (tile_136 // 4 == string_to_34_tile(honors="3"))
            or (tile_136 // 4 == string_to_34_tile(honors="5"))
            or (tile_136 // 4 == string_to_34_tile(honors="6"))
            or (tile_136 // 4 == string_to_34_tile(honors="7"))
        ):
            assert bonus_danger
        else:
            assert not bonus_danger
