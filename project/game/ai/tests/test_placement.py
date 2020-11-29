from game.ai.placement import Placement
from game.table import Table
from utils.decisions_logger import MeldPrint
from utils.test_helpers import make_meld, string_to_136_array, string_to_136_tile


def test_placement_evaluation():
    table = Table()
    player = table.player

    # very comfortable first
    player.scores = 82000
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 6000

    placement = player.ai.placement._get_placement_evaluation(player.ai.placement.get_current_placement())
    assert placement == Placement.VERY_COMFORTABLE_FIRST


def test_placement():
    table = Table()
    player = table.player

    player.scores = 82000
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 6000

    placement = player.ai.placement.get_current_placement()
    assert placement["place"] == 1
    assert placement["diff_with_1st"] == 0
    assert placement["diff_with_2nd"] == 76000
    assert placement["diff_with_3rd"] == 76000
    assert placement["diff_with_4th"] == 76000
    assert placement["diff_with_next_up"] == 0
    assert placement["diff_with_next_down"] == 76000

    player.scores = 22000
    i = -1
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 24000 + i * 6000
            i += 1

    placement = player.ai.placement.get_current_placement()
    assert placement["place"] == 3
    assert placement["diff_with_1st"] == 8000
    assert placement["diff_with_2nd"] == 2000
    assert placement["diff_with_3rd"] == 0
    assert placement["diff_with_4th"] == 4000
    assert placement["diff_with_next_up"] == 2000
    assert placement["diff_with_next_down"] == 4000

    player.scores = 1000
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 33000

    placement = player.ai.placement.get_current_placement()
    assert placement["place"] == 4
    assert placement["diff_with_1st"] == 32000
    assert placement["diff_with_2nd"] == 32000
    assert placement["diff_with_3rd"] == 32000
    assert placement["diff_with_4th"] == 0
    assert placement["diff_with_next_up"] == 32000
    assert placement["diff_with_next_down"] == 0


def test_minimal_cost():
    table = Table()
    player = table.player

    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    player.scores = 22000
    i = -1
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 24000 + i * 6000
            i += 1

    minimal_cost = player.ai.placement.get_minimal_cost_needed()
    assert minimal_cost == 0

    player.scores = 1000
    for enemy in table.players:
        if enemy != player:
            enemy.scores = 33000

    minimal_cost = player.ai.placement.get_minimal_cost_needed()
    assert minimal_cost == 32000


def test_skip_ron():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    # 1900 to 3rd place
    player.scores = 20100
    assert table.players[0] == player
    table.players[1].scores = 22000
    table.players[2].scores = 26000
    table.players[3].scores = 30900

    minimal_cost = player.ai.placement.get_minimal_cost_needed()
    assert minimal_cost == 1900

    tiles = string_to_136_array(man="23488", sou="34678", pin="567")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, pin="567"))
    table.player.round_step = 14

    # we should not call ron 1000 from 2nd place as it leaves us on 4th
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 2)

    # ron 2000 from 2nd place is ok, it's enough to get to 3rd
    assert player.should_call_win(string_to_136_tile(sou="2"), False, 2)

    # ron 1000 from 3rd place is ok too
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)

    # ron 1000 from 1st place is ok too as it moves us to west round
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 3)

    # ron 2000 from 1st place is ok, checking just to be sure
    assert player.should_call_win(string_to_136_tile(sou="2"), False, 3)


def test_dont_skip_ron_if_dealer():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 0
    player.dealer_seat = 0

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    player.scores = 16100
    assert table.players[0] == player
    table.players[1].scores = 24000
    table.players[2].scores = 26000
    table.players[3].scores = 35900

    tiles = string_to_136_array(man="23488", sou="34678", pin="567")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, pin="567"))
    table.player.round_step = 14

    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 2)
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 3)


def test_take_ron_for_west():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    tiles = string_to_136_array(man="23488", sou="34678", pin="567")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, pin="567"))
    table.player.round_step = 14

    player.scores = 20100
    assert table.players[0] == player
    table.players[1].scores = 22000
    table.players[2].scores = 26000
    table.players[3].scores = 29900

    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 2)
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 3)

    player.scores = 20100
    assert table.players[0] == player
    table.players[1].scores = 22000
    table.players[2].scores = 30100
    table.players[3].scores = 31000

    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 2)
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 3)


def test_skip_ron_in_west_4():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 11
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    tiles = string_to_136_array(man="23488", sou="34678", pin="567")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, pin="567"))
    table.player.round_step = 14

    player.scores = 20100
    assert table.players[0] == player
    table.players[1].scores = 22000
    table.players[2].scores = 26000
    table.players[3].scores = 29900

    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 2)
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 3)


def test_skip_ron_wind_placement():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    tiles = string_to_136_array(man="23488", sou="34678", pin="567")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, pin="567"))
    table.player.round_step = 14

    player.scores = 21000
    assert table.players[0] == player
    table.players[1].scores = 22000
    table.players[2].scores = 30100
    table.players[3].scores = 31000

    player.first_seat = 0
    table.players[1].first_seat = 1

    assert player.ai.placement.get_minimal_cost_needed() == 1000

    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 2)
    assert player.should_call_win(string_to_136_tile(sou="5"), False, 3)

    player.first_seat = 1
    table.players[1].first_seat = 0

    assert player.ai.placement.get_minimal_cost_needed() == 1100

    assert player.should_call_win(string_to_136_tile(sou="5"), False, 1)
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 2)
    assert not player.should_call_win(string_to_136_tile(sou="5"), False, 3)


def test_skip_cheap_meld_tempai():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="2"))

    tiles = string_to_136_array(man="3488", sou="334678", pin="678")
    table.player.init_hand(tiles)
    table.player.round_step = 12

    player.scores = 18000
    assert table.players[0] == player
    table.players[1].scores = 28000
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    # it's too cheap, let's not open
    tile = string_to_136_tile(sou="2")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # now this is the cost we might win with
    tile = string_to_136_tile(sou="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None


def test_skip_cheap_meld_1_shanten():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="2"))

    tiles = string_to_136_array(man="3488", sou="334678", pin="268")
    table.player.init_hand(tiles)
    table.player.round_step = 12

    player.scores = 18000
    assert table.players[0] == player
    table.players[1].scores = 28000
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    # it's too cheap, let's not open
    tile = string_to_136_tile(sou="2")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # now this is the cost we might win with
    tile = string_to_136_tile(sou="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None


def test_skip_cheap_meld_2_shanten():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="2"))

    tiles = string_to_136_array(man="34889", sou="33468", pin="268")
    table.player.init_hand(tiles)
    table.player.round_step = 12

    player.scores = 18000
    assert table.players[0] == player
    table.players[1].scores = 28000
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    # it's too cheap, let's not open
    tile = string_to_136_tile(sou="2")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # now this is the cost we might win with
    tile = string_to_136_tile(sou="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None


def test_skip_cheap_meld_1_shanten_can_move_to_west():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="2"))

    tiles = string_to_136_array(man="3488", sou="334678", pin="268")
    table.player.init_hand(tiles)
    table.player.round_step = 12

    player.scores = 18000
    assert table.players[0] == player
    table.players[1].scores = 28000
    table.players[2].scores = 29000
    table.players[3].scores = 31000

    # it's cheap, but with ron from first place we can move game to west round, so let's do it
    tile = string_to_136_tile(sou="2")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # now this is the cost we might win with
    tile = string_to_136_tile(sou="3")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None


def test_take_cheap_meld_tempai():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(man="2"))

    tiles = string_to_136_array(man="23789", sou="3789", pin="99", honors="33")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 20900
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    # no yaku, skip
    tile = string_to_136_tile(man="4")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # now this is the cost we might win with
    tile = string_to_136_tile(man="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # now this is not enough
    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 30900
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    tile = string_to_136_tile(man="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_take_cheap_meld_tempai_tanyao_not_activated():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    # tanyao is not activated due to tanyao rules but we don't care and take this meld
    tiles = string_to_136_array(man="23678", sou="3567", pin="2257")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 20900
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    # no yaku, skip
    tile = string_to_136_tile(man="1")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # now this is the cost we might win with
    tile = string_to_136_tile(man="4")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # now this is not enough
    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 30900
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    tile = string_to_136_tile(man="4")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_take_cheap_meld_yakuhai_tempai():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    tiles = string_to_136_array(man="23678", sou="3567", pin="22", honors="55")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 20900
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    # bad atodzuke - skip
    tile = string_to_136_tile(pin="2")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # now this is the cost we might win with
    tile = string_to_136_tile(honors="5")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # now this is not enough
    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 30900
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    tile = string_to_136_tile(honors="5")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_take_cheap_meld_yakuhai_1_shanten():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    tiles = string_to_136_array(man="236778", sou="357", pin="22", honors="55")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 20900
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    # bad atodzuke - skip
    tile = string_to_136_tile(pin="2")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # now this is the cost we might win with
    tile = string_to_136_tile(honors="5")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # now this is not enough
    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 30900
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    tile = string_to_136_tile(honors="5")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_must_push_4th():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    # we have 1-shanten with no doras, but we must push because we have 4th place in oorasu
    tiles = string_to_136_array(man="3488", sou="334678", pin="456")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 18000
    assert table.players[0] == player
    table.players[1].scores = 28000
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    enemy_seat = 2
    table.add_called_riichi_step_one(enemy_seat)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1

    assert player.ai.placement.must_push(threatening_players, 0, 1)


def test_must_push_3rd_and_last_place_riichi():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    # we have 1-shanten with no doras, but we must push because we have 4th place in oorasu
    tiles = string_to_136_array(man="3488", sou="334678", pin="456")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 18000
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    enemy_seat = 1
    table.add_called_riichi_step_one(enemy_seat)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1

    assert player.ai.placement.must_push(threatening_players, 0, 1)


def test_must_push_3rd_and_1st_place_riichi():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    # we have 1-shanten with no doras, but we must push because we have 4th place in oorasu
    tiles = string_to_136_array(man="3488", sou="334678", pin="456")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 18000
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    enemy_seat = 3
    table.add_called_riichi_step_one(enemy_seat)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1

    assert not player.ai.placement.must_push(threatening_players, 0, 1)


def test_must_push_3rd_and_multiple_riichi():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    # we have 1-shanten with no doras, but we must push because we have 4th place in oorasu
    tiles = string_to_136_array(man="3488", sou="334678", pin="456")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 20000
    assert table.players[0] == player
    table.players[1].scores = 18000
    table.players[2].scores = 35000
    table.players[3].scores = 40000

    table.add_called_riichi_step_one(1)
    table.add_called_riichi_step_one(3)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 2

    assert not player.ai.placement.must_push(threatening_players, 0, 1)


def test_must_push_2nd():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    # we have 1-shanten with no doras, but we must push because we have 4th place in oorasu
    tiles = string_to_136_array(man="3488", sou="334678", pin="456")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 42000
    assert table.players[0] == player
    table.players[1].scores = 45000
    table.players[2].scores = 5000
    table.players[3].scores = 10000

    enemy_seat = 3
    table.add_called_riichi_step_one(enemy_seat)
    table.count_of_riichi_sticks += 1

    # we don't care about 3rd place riichi we just push
    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1

    # 2600 and a riichi stick is enough
    assert player.ai.placement.must_push(threatening_players, 0, 1, 2600)


def test_must_push_1st_and_2nd_place_riichi():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    # we have 1-shanten with no doras, but we must push because we have 4th place in oorasu
    tiles = string_to_136_array(man="3488", sou="334678", pin="456")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 45000
    assert table.players[0] == player
    table.players[1].scores = 42000
    table.players[2].scores = 5000
    table.players[3].scores = 8000

    enemy_seat = 1
    table.add_called_riichi_step_one(enemy_seat)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1
    assert player.ai.placement.must_push(threatening_players, 0, 1)


def test_must_push_1st_and_4th_place_riichi():
    table = Table()
    player = table.player
    table.has_aka_dora = True
    table.has_open_tanyao = True
    # orasu
    table.round_wind_number = 7
    table.dealer_seat = 1
    player.dealer_seat = 1

    table.add_dora_indicator(string_to_136_tile(sou="1"))

    # we have 1-shanten with no doras, but we must push because we have 4th place in oorasu
    tiles = string_to_136_array(man="3488", sou="334678", pin="456")
    table.player.init_hand(tiles)
    table.player.round_step = 5

    player.scores = 45000
    assert table.players[0] == player
    table.players[1].scores = 42000
    table.players[2].scores = 5000
    table.players[3].scores = 8000

    enemy_seat = 3
    table.add_called_riichi_step_one(enemy_seat)

    threatening_players = table.player.ai.defence.get_threatening_players()
    assert len(threatening_players) == 1

    assert not player.ai.placement.must_push(threatening_players, 0, 1)
