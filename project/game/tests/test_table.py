from game.table import Table
from mahjong.constants import EAST, FIVE_RED_MAN, FIVE_RED_PIN, FIVE_RED_SOU, NORTH, SOUTH, WEST
from utils.test_helpers import string_to_136_tile


def test_init_hand():
    table = Table()
    tiles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    table.player.init_hand(tiles)

    assert len(table.player.tiles) == 13


def test_init_round():
    table = Table()

    round_wind_number = 4
    count_of_honba_sticks = 2
    count_of_riichi_sticks = 3
    dora_indicator = 126
    dealer = 3
    scores = [250, 250, 250, 250]

    table.init_round(round_wind_number, count_of_honba_sticks, count_of_riichi_sticks, dora_indicator, dealer, scores)

    assert table.round_wind_number == round_wind_number
    assert table.count_of_honba_sticks == count_of_honba_sticks
    assert table.count_of_riichi_sticks == count_of_riichi_sticks
    assert table.dora_indicators[0] == dora_indicator
    assert table.get_player(dealer).is_dealer is True
    assert table.get_player(dealer).scores == 25000

    dealer = 2
    table.player.in_tempai = True
    table.player.in_riichi = True
    table.init_round(round_wind_number, count_of_honba_sticks, count_of_riichi_sticks, dora_indicator, dealer, scores)

    # test that we reinit round properly
    assert table.get_player(3).is_dealer is False
    assert table.player.in_tempai is False
    assert table.player.in_riichi is False
    assert table.get_player(dealer).is_dealer is True


def test_set_scores():
    table = Table()
    table.init_round(0, 0, 0, 0, 0, [])
    scores = [230, 110, 55, 405]

    table.set_players_scores(scores)

    assert table.get_player(0).scores == 23000
    assert table.get_player(1).scores == 11000
    assert table.get_player(2).scores == 5500
    assert table.get_player(3).scores == 40500


def test_set_scores_and_uma():
    table = Table()
    table.init_round(0, 0, 0, 0, 0, [])
    scores = [230, 110, 55, 405]
    uma = [-17, 3, 48, -34]

    table.set_players_scores(scores, uma)

    assert table.get_player(0).scores == 23000
    assert table.get_player(0).uma == (-17)
    assert table.get_player(1).scores == 11000
    assert table.get_player(1).uma == 3
    assert table.get_player(2).scores == 5500
    assert table.get_player(2).uma == 48
    assert table.get_player(3).scores == 40500
    assert table.get_player(3).uma == (-34)


def test_set_scores_and_recalculate_player_position():
    table = Table()
    table.init_round(0, 0, 0, 0, 0, [])

    assert table.get_player(0).first_seat == 0
    assert table.get_player(1).first_seat == 1
    assert table.get_player(2).first_seat == 2
    assert table.get_player(3).first_seat == 3

    scores = [230, 110, 55, 405]
    table.set_players_scores(scores)

    assert table.get_player(0).position == 2
    assert table.get_player(1).position == 3
    assert table.get_player(2).position == 4
    assert table.get_player(3).position == 1

    scores = [110, 110, 405, 405]
    table.set_players_scores(scores)

    assert table.get_player(0).position == 3
    assert table.get_player(1).position == 4
    assert table.get_player(2).position == 1
    assert table.get_player(3).position == 2


def test_set_names_and_ranks():
    table = Table()
    table.init_round(0, 0, 0, 0, 0, [])

    values = [
        {"name": "NoName", "rank": "新人"},
        {"name": "o2o2", "rank": "3級"},
        {"name": "shimmmmm", "rank": "三段"},
        {"name": "川海老", "rank": "9級"},
    ]

    table.set_players_names_and_ranks(values)

    assert table.get_player(0).name == "NoName"
    assert table.get_player(0).rank == "新人"
    assert table.get_player(3).name == "川海老"
    assert table.get_player(3).rank == "9級"


def test_is_dora():
    table = Table()
    table.init_round(0, 0, 0, 0, 0, [])

    table.dora_indicators = [string_to_136_tile(sou="1")]
    assert table.is_dora(string_to_136_tile(sou="2"))

    table.dora_indicators = [string_to_136_tile(sou="9")]
    assert table.is_dora(string_to_136_tile(sou="1"))

    table.dora_indicators = [string_to_136_tile(pin="9")]
    assert table.is_dora(string_to_136_tile(pin="1"))

    table.dora_indicators = [string_to_136_tile(man="9")]
    assert table.is_dora(string_to_136_tile(man="1"))

    table.dora_indicators = [string_to_136_tile(man="5")]
    assert table.is_dora(string_to_136_tile(man="6"))

    table.dora_indicators = [string_to_136_tile(honors="1")]
    assert table.is_dora(string_to_136_tile(honors="2"))

    table.dora_indicators = [string_to_136_tile(honors="2")]
    assert table.is_dora(string_to_136_tile(honors="3"))

    table.dora_indicators = [string_to_136_tile(honors="3")]
    assert table.is_dora(string_to_136_tile(honors="4"))

    table.dora_indicators = [string_to_136_tile(honors="4")]
    assert table.is_dora(string_to_136_tile(honors="1"))

    table.dora_indicators = [string_to_136_tile(honors="5")]
    assert table.is_dora(string_to_136_tile(honors="6"))

    table.dora_indicators = [string_to_136_tile(honors="6")]
    assert table.is_dora(string_to_136_tile(honors="7"))

    table.dora_indicators = [string_to_136_tile(honors="7")]
    assert table.is_dora(string_to_136_tile(honors="5"))

    table.dora_indicators = [string_to_136_tile(pin="1")]
    assert not table.is_dora(string_to_136_tile(sou="2"))

    table.has_open_tanyao = True

    # red five man
    assert table.is_dora(FIVE_RED_MAN)

    # red five pin
    assert table.is_dora(FIVE_RED_PIN)

    # red five sou
    assert table.is_dora(FIVE_RED_SOU)


def test_round_wind():
    table = Table()

    table.init_round(0, 0, 0, 0, 0, [])
    assert table.round_wind_tile == EAST

    table.init_round(3, 0, 0, 0, 0, [])
    assert table.round_wind_tile == EAST

    table.init_round(7, 0, 0, 0, 0, [])
    assert table.round_wind_tile == SOUTH

    table.init_round(11, 0, 0, 0, 0, [])
    assert table.round_wind_tile == WEST

    table.init_round(12, 0, 0, 0, 0, [])
    assert table.round_wind_tile == NORTH
