from game.ai.defence.yaku_analyzer.honitsu import HonitsuAnalyzer
from game.ai.defence.yaku_analyzer.tanyao import TanyaoAnalyzer
from game.ai.defence.yaku_analyzer.yakuhai import YakuhaiAnalyzer
from game.ai.helpers.defence import EnemyDanger
from game.table import Table
from mahjong.constants import HONOR_INDICES, TERMINAL_INDICES
from mahjong.meld import Meld
from utils.test_helpers import make_meld, string_to_136_tile


def test_is_threatening_and_riichi():
    table = Table()

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 2
    table.add_called_riichi(enemy_seat)

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].player.seat == enemy_seat
    assert threatening_players[0].threat_reason == EnemyDanger.THREAT_RIICHI


def test_is_threatening_and_dora_pon():
    table = Table()

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 2
    table.add_called_meld(enemy_seat, make_meld(Meld.PON, man="333"))
    table.player.round_step = 7

    # simple pon it is no threat
    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    # dora pon is threat
    table.add_dora_indicator(string_to_136_tile(man="2"))
    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].player.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_OPEN_HAND_AND_MULTIPLE_DORA["id"]


def test_is_threatening_and_closed_dora_kan():
    table = Table()

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 2
    table.add_called_meld(enemy_seat, make_meld(Meld.KAN, is_open=False, man="3333"))
    table.player.round_step = 7

    # simple pon it is no threat
    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    # dora kan is threat
    table.add_dora_indicator(string_to_136_tile(man="2"))
    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].player.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_OPEN_HAND_AND_MULTIPLE_DORA["id"]


def test_is_threatening_and_two_open_yakuhai_melds():
    table = Table()

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    # south player
    enemy_seat = 1
    # south round
    table.round_wind_number = 4

    table.add_called_meld(enemy_seat, make_meld(Meld.PON, honors="222"))
    table.add_called_meld(enemy_seat, make_meld(Meld.CHI, man="123"))
    table.player.round_step = 2

    # double wind is not enough
    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    # with one dora in enemy melds we can start think about threat
    # it will be 3 han
    table.add_dora_indicator(string_to_136_tile(man="1"))
    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].player.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND["id"]


def test_is_threatening_and_two_open_tanyao_melds():
    table = Table()

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 2
    table.add_called_meld(enemy_seat, make_meld(Meld.PON, pin="234"))
    table.add_called_meld(enemy_seat, make_meld(Meld.CHI, sou="333"))
    table.player.round_step = 2

    # tanyao without dor is not threat
    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    # and now it is threat
    table.add_dora_indicator(string_to_136_tile(pin="1"))
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].player.seat == enemy_seat
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND["id"]


def test_is_threatening_and_honitsu_hand():
    table = Table()

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 0

    enemy_seat = 1
    table.add_called_meld(enemy_seat, make_meld(Meld.PON, pin="567"))
    table.add_called_meld(enemy_seat, make_meld(Meld.CHI, pin="123"))
    table.add_called_meld(enemy_seat, make_meld(Meld.CHI, pin="345"))

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), False)

    threatening_players = table.player.ai.defence._get_threatening_players()
    assert len(threatening_players) == 1
    assert threatening_players[0].threat_reason["id"] == EnemyDanger.THREAT_HONITSU["id"]


def test_tanyao_dangerous_tiles():
    table = Table()

    tanyao = TanyaoAnalyzer(table.player)
    dangerous_tiles = tanyao.get_dangerous_tiles()

    assert len(dangerous_tiles) == 21
    assert all([(x in TERMINAL_INDICES) for x in dangerous_tiles]) is False
    assert all([(x in HONOR_INDICES) for x in dangerous_tiles]) is False


def test_yakuhai_dangerous_tiles():
    table = Table()

    yakuhai = YakuhaiAnalyzer(table.player)
    dangerous_tiles = yakuhai.get_dangerous_tiles()

    assert len(dangerous_tiles) == 34


def test_honitsu_dangerous_tiles():
    table = Table()

    enemy_seat = 2
    honitsu = HonitsuAnalyzer(table.get_player(enemy_seat))

    table.add_called_meld(enemy_seat, make_meld(Meld.PON, pin="567"))
    table.add_called_meld(enemy_seat, make_meld(Meld.CHI, pin="123"))
    table.add_called_meld(enemy_seat, make_meld(Meld.CHI, pin="345"))

    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="5"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="8"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(sou="9"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(man="1"), False)
    table.add_discarded_tile(enemy_seat, string_to_136_tile(pin="1"), False)

    assert honitsu.is_yaku_active()
    dangerous_tiles = honitsu.get_dangerous_tiles()

    # 9 from suit
    # 7 from honors
    assert len(dangerous_tiles) == 16
