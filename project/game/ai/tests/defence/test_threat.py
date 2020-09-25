from game.ai.helpers.defence import EnemyDanger
from game.table import Table
from mahjong.meld import Meld
from utils.test_helpers import make_meld, string_to_136_array, string_to_136_tile


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


def test_threatening_riichi_player_and_default_hand_cost():
    table = Table()
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)

    # non dealer
    threatening_player = table.player.ai.defence._get_threatening_players()[0]
    assert threatening_player.player.seat == enemy_seat
    assert threatening_player.calculate_hand_cost() == 3900

    # dealer
    threatening_player.player.dealer_seat = enemy_seat
    assert threatening_player.calculate_hand_cost() == 5800


def test_threatening_riichi_player_and_not_early_hand_bonus():
    table = Table()
    enemy_seat = 2
    table.add_called_riichi(enemy_seat)
    discards = string_to_136_array(sou="1111222")
    for discard in discards:
        table.add_discarded_tile(enemy_seat, discard, False)

    # +1 scale for riichi on 6+ turn
    threatening_player = table.player.ai.defence._get_threatening_players()[0]
    assert threatening_player.player.seat == enemy_seat
    assert threatening_player.calculate_hand_cost() == 5200


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
    threatening_player = table.player.ai.defence._get_threatening_players()[0]
    assert threatening_player.player.seat == enemy_seat
    assert threatening_player.calculate_hand_cost() == 5200
