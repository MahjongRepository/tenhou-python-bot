from game.ai.defence.yaku_analyzer.honitsu import HonitsuAnalyzer
from game.ai.helpers.defence import EnemyDanger
from game.table import Table
from mahjong.utils import is_honor
from utils.decisions_logger import MeldPrint
from utils.test_helpers import make_meld, string_to_136_array, string_to_136_tile


def test_is_threatening_and_riichi():
    table = Table()

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 2
    table.add_called_riichi(enemy_seat)

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

    # simple pon it is no threat
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    # dora pon is threat
    table.add_dora_indicator(string_to_136_tile(man="2"))
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_OPEN_HAND_AND_MULTIPLE_DORA["id"]
    assert threatening_players[0].assumed_hand_cost == 8000


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
    assert threatening_players[0].assumed_hand_cost == 3900

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

    # tanyao without dor is not threat
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    # and now it is threat
    table.add_dora_indicator(string_to_136_tile(pin="1"))
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND["id"]
    assert threatening_players[0].assumed_hand_cost == 3900

    for tile_136 in range(0, 136):
        bonus_danger = threatening_players[0].threat_reason.get("active_yaku")[0].get_bonus_danger(tile_136, 1)
        assert not bonus_danger


def test_is_threatening_and_honitsu_hand():
    table = Table()
    table.add_dora_indicator(string_to_136_tile(pin="1"))

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 1
    table.add_called_meld(enemy_seat, make_meld(MeldPrint.PON, pin="567"))
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
    assert threatening_players[0].assumed_hand_cost == 3900
    assert threatening_players[0].threat_reason["active_yaku"][0].id == HonitsuAnalyzer.id

    for tile_136 in range(0, 136):
        bonus_danger = threatening_players[0].threat_reason.get("active_yaku")[0].get_bonus_danger(tile_136, 1)
        if is_honor(tile_136 // 4):
            assert bonus_danger
        else:
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

    table.add_dora_indicator(string_to_136_tile(pin="1"))

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].enemy.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND["id"]
    assert threatening_players[0].assumed_hand_cost == 8000


def test_threatening_riichi_player_and_default_hand_cost():
    table = Table()
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.assumed_hand_cost == 3900

    # dealer
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.assumed_hand_cost == 5800


def test_threatening_riichi_player_and_not_early_hand_bonus():
    table = Table()
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)
    discards = string_to_136_array(sou="1111222")
    for discard in discards:
        table.add_discarded_tile(enemy_seat, discard, False)

    # +1 scale for riichi on 6+ turn
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.assumed_hand_cost == 5200


def test_threatening_riichi_player_and_not_visible_dora():
    table = Table()
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)
    table.add_dora_indicator(string_to_136_tile(sou="2"))
    table.has_aka_dora = True

    discards = string_to_136_array(sou="33")
    for discard in discards:
        table.add_discarded_tile(enemy_seat, discard, False)

    # +1 scale for riichi on 6+ turn
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.assumed_hand_cost == 5200


def test_threatening_riichi_player_with_kan():
    table = Table()
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, man="3333"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.assumed_hand_cost == 5200

    # dealer
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.assumed_hand_cost == 7700


def test_threatening_riichi_player_with_kan_aka():
    table = Table()
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)
    table.has_aka_dora = True

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, man="5505"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.assumed_hand_cost == 8000

    # dealer
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.assumed_hand_cost == 12000


def test_threatening_riichi_player_with_dora_kan():
    table = Table()
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)

    table.add_dora_indicator(string_to_136_tile(man="2"))

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, man="3333"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.assumed_hand_cost == 16000

    # dealer
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.assumed_hand_cost == 24000


def test_threatening_riichi_player_with_yakuhai_kan():
    table = Table()
    enemy_seat = 2
    table.round_wind_number = 1
    table.add_called_riichi(enemy_seat)

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, honors="1111"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.assumed_hand_cost == 8000


def test_threatening_riichi_player_with_double_yakuhai_kan():
    table = Table()
    enemy_seat = 2
    table.round_wind_number = 1
    table.add_called_riichi(enemy_seat)

    table.add_called_meld(enemy_seat, make_meld(MeldPrint.KAN, is_open=False, honors="1111"))

    # non dealer
    threatening_player = table.player.ai.defence.get_threatening_players()[0]
    threatening_player.enemy.dealer_seat = enemy_seat
    assert threatening_player.enemy.seat == enemy_seat
    assert threatening_player.assumed_hand_cost == 18000


def test_number_of_unverified_suji():
    table = Table()
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)

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
