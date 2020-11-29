from game.ai.strategies.main import BaseStrategy
from game.ai.strategies.tanyao import TanyaoStrategy
from game.table import Table
from mahjong.constants import FIVE_RED_PIN, FIVE_RED_SOU
from utils.decisions_logger import MeldPrint
from utils.test_helpers import make_meld, string_to_136_array, string_to_136_tile, tiles_to_string


def test_should_activate_strategy_and_terminal_pon_sets():
    table = _make_table()

    strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)

    tiles = string_to_136_array(sou="222", man="3459", pin="233", honors="111")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(sou="222", man="3459", pin="233999")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(sou="222", man="3459", pin="233444")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is True


def test_should_activate_strategy_and_terminal_pairs():
    table = _make_table()
    strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)

    tiles = string_to_136_array(sou="222", man="3459", pin="2399", honors="11")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(sou="22258", man="3566", pin="2399")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is True


def test_should_activate_strategy_and_valued_pair():
    table = _make_table()
    strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)

    tiles = string_to_136_array(man="23446679", sou="222", honors="55")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(man="23446679", sou="222", honors="22")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is True


def test_should_activate_strategy_and_chitoitsu_like_hand():
    table = _make_table()
    strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)

    tiles = string_to_136_array(sou="223388", man="2244", pin="6687")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is True


def test_should_activate_strategy_and_already_completed_sided_set():
    table = _make_table()
    strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)

    tiles = string_to_136_array(sou="123234", man="2349", pin="234")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(sou="234789", man="2349", pin="234")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(sou="234", man="1233459", pin="234")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(sou="234", man="2227899", pin="234")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(sou="234", man="2229", pin="122334")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(sou="234", man="2229", pin="234789")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is False

    tiles = string_to_136_array(sou="223344", man="2229", pin="234")
    table.player.init_hand(tiles)
    assert strategy.should_activate_strategy(table.player.tiles) is True


def test_suitable_tiles():
    table = _make_table()
    strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)

    tile = string_to_136_tile(man="1")
    assert strategy.is_tile_suitable(tile) is False

    tile = string_to_136_tile(pin="1")
    assert strategy.is_tile_suitable(tile) is False

    tile = string_to_136_tile(sou="9")
    assert strategy.is_tile_suitable(tile) is False

    tile = string_to_136_tile(honors="1")
    assert strategy.is_tile_suitable(tile) is False

    tile = string_to_136_tile(honors="6")
    assert strategy.is_tile_suitable(tile) is False

    tile = string_to_136_tile(man="2")
    assert strategy.is_tile_suitable(tile) is True

    tile = string_to_136_tile(pin="5")
    assert strategy.is_tile_suitable(tile) is True

    tile = string_to_136_tile(sou="8")
    assert strategy.is_tile_suitable(tile) is True


def test_dont_open_hand_with_high_shanten():
    table = _make_table()
    # with 4 shanten we don't need to aim for open tanyao
    tiles = string_to_136_array(man="269", pin="247", sou="2488", honors="123")
    tile = string_to_136_tile(sou="3")
    table.player.init_hand(tiles)
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is None

    # with 3 shanten we can open a hand
    tiles = string_to_136_array(man="236", pin="247", sou="2488", honors="123")
    tile = string_to_136_tile(sou="3")
    table.player.init_hand(tiles)
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None


def test_dont_open_hand_with_not_suitable_melds():
    table = _make_table()
    tiles = string_to_136_array(man="22255788", sou="3479", honors="3")
    tile = string_to_136_tile(sou="8")
    table.player.init_hand(tiles)
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is None


def test_open_hand_and_discard_tiles_logic():
    table = _make_table()
    tiles = string_to_136_array(man="22234", sou="238", pin="256", honors="44")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(sou="4")
    meld, discard_option = table.player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string([discard_option.tile_to_discard_136]) == "4z"

    tiles = string_to_136_array(man="22234", sou="2348", pin="256", honors="44")
    table.player.init_hand(tiles)
    table.player.add_called_meld(meld)
    table.player.discard_tile(discard_option)

    tile = string_to_136_tile(pin="5")
    table.player.draw_tile(tile)
    tile_to_discard, _ = table.player.discard_tile()

    assert tiles_to_string([tile_to_discard]) == "4z"


def test_open_hand_and_discard_tiles_logic_advanced():
    # we should choose between one of the ryanmens to discard
    # in this case - discard the one that leads us to atodzuke and has less tanyao ukeire
    # despite the fact that general ukeire is higher
    table = _make_table()
    table.add_discarded_tile(2, string_to_136_tile(pin="4"), False)
    table.add_discarded_tile(2, string_to_136_tile(pin="7"), False)
    table.add_discarded_tile(2, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(2, string_to_136_tile(sou="7"), False)

    tiles = string_to_136_array(man="236777", sou="56", pin="22256")
    table.player.init_hand(tiles)
    meld = make_meld(MeldPrint.PON, pin="222")
    table.player.add_called_meld(meld)
    tile = string_to_136_tile(man="6")
    table.player.draw_tile(tile)
    tile_to_discard, _ = table.player.discard_tile()
    assert tiles_to_string([tile_to_discard]) == "2m" or tiles_to_string([tile_to_discard]) == "3m"

    # now same situation, but better ryanmen is no atodzuke
    table = _make_table()
    table.add_discarded_tile(2, string_to_136_tile(pin="4"), False)
    table.add_discarded_tile(2, string_to_136_tile(pin="7"), False)
    table.add_discarded_tile(2, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(2, string_to_136_tile(sou="7"), False)

    tiles = string_to_136_array(man="346777", sou="56", pin="22256")
    table.player.init_hand(tiles)
    meld = make_meld(MeldPrint.PON, pin="222")
    table.player.add_called_meld(meld)
    tile = string_to_136_tile(man="6")
    table.player.draw_tile(tile)
    tile_to_discard, _ = table.player.discard_tile()
    assert (
        tiles_to_string([tile_to_discard]) == "5s"
        or tiles_to_string([tile_to_discard]) == "6s"
        or tiles_to_string([tile_to_discard]) == "5p"
        or tiles_to_string([tile_to_discard]) == "6p"
    )

    # now same situation as the first one, but ryanshanten
    table = _make_table()
    table.add_discarded_tile(2, string_to_136_tile(pin="4"), False)
    table.add_discarded_tile(2, string_to_136_tile(pin="7"), False)
    table.add_discarded_tile(2, string_to_136_tile(sou="4"), False)
    table.add_discarded_tile(2, string_to_136_tile(sou="7"), False)
    table.add_discarded_tile(2, string_to_136_tile(man="5"), False)
    table.add_discarded_tile(2, string_to_136_tile(man="8"), False)

    tiles = string_to_136_array(man="2367", sou="2356", pin="22256")
    table.player.init_hand(tiles)
    meld = make_meld(MeldPrint.PON, pin="222")
    table.player.add_called_meld(meld)
    tile = string_to_136_tile(man="8")
    table.player.draw_tile(tile)
    tile_to_discard, _ = table.player.discard_tile()
    assert (
        tiles_to_string([tile_to_discard]) == "2m"
        or tiles_to_string([tile_to_discard]) == "3m"
        or tiles_to_string([tile_to_discard]) == "2s"
        or tiles_to_string([tile_to_discard]) == "3s"
    )


def test_dont_count_pairs_in_already_opened_hand():
    table = _make_table()
    tiles = string_to_136_array(man="33556788", sou="22266")
    table.player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, sou="222")
    table.player.add_called_meld(meld)

    tile = string_to_136_tile(sou="6")
    meld, _ = table.player.try_to_call_meld(tile, False)
    # even if it looks like chitoitsu we can open hand and get tempai here
    assert meld is not None


def test_we_cant_win_with_this_hand():
    table = _make_table()
    tiles = string_to_136_array(man="22277", sou="23", pin="233445")
    table.player.init_hand(tiles)
    meld = make_meld(MeldPrint.CHI, pin="234")
    table.player.add_called_meld(meld)

    table.player.draw_tile(string_to_136_tile(sou="1"))
    discard, _ = table.player.discard_tile()
    # but for already open hand we cant do tsumo
    # because we don't have a yaku here
    # so, let's do tsumogiri
    assert table.player.ai.shanten == 0
    assert tiles_to_string([discard]) == "1s"


def test_choose_correct_waiting():
    table = _make_table()
    tiles = string_to_136_array(man="222678", sou="234", pin="3588")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(pin="2"))

    _assert_tanyao(table.player)

    # discard 5p and riichi
    discard, _ = table.player.discard_tile()
    assert tiles_to_string([discard]) == "5p"

    meld = make_meld(MeldPrint.CHI, man="234")
    table.player.add_called_meld(meld)

    tiles = string_to_136_array(man="234888", sou="234", pin="3588")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(pin="2"))

    # it is not a good idea to wait on 1-4, since we can't win on 1 with open hand
    # so let's continue to wait on 4 only
    discard, _ = table.player.discard_tile()
    assert tiles_to_string([discard]) == "2p"

    table = _make_table()
    player = table.player

    meld = make_meld(MeldPrint.CHI, man="678")
    player.add_called_meld(meld)

    tiles = string_to_136_array(man="222678", sou="234", pin="2388")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(sou="7"))

    # we can wait only on 1-4, so let's do it even if we can't get yaku on 1
    discard, _ = player.discard_tile()
    assert tiles_to_string([discard]) == "7s"


def test_choose_balanced_ukeire_in_1_shanten():
    table = _make_table()
    player = table.player

    meld = make_meld(MeldPrint.CHI, man="678")
    player.add_called_meld(meld)

    tiles = string_to_136_array(man="22678", sou="234568", pin="45")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(man="2"))

    _assert_tanyao(player)

    # there are lost of options to avoid atodzuke and even if it is atodzuke,
    # it is still a good one, so let's choose more efficient 8s discard instead of 2s
    discard, _ = player.discard_tile()
    assert tiles_to_string([discard]) == "8s"


def test_choose_pseudo_atodzuke():
    table = _make_table()
    table.has_aka_dora = False
    player = table.player

    # one tile is dora indicator and 3 are out
    # so this 1-4 wait is not atodzuke
    for _ in range(0, 3):
        table.add_discarded_tile(1, string_to_136_tile(pin="1"), False)

    meld = make_meld(MeldPrint.CHI, man="678")
    player.add_called_meld(meld)

    tiles = string_to_136_array(man="222678", sou="23488", pin="35")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(pin="2"))

    _assert_tanyao(player)

    discard, _ = player.discard_tile()
    assert tiles_to_string([discard]) == "5p"


def test_choose_correct_waiting_and_first_opened_meld():
    table = _make_table()
    tiles = string_to_136_array(man="2337788", sou="222", pin="234")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(man="8")
    meld, tile_to_discard = table.player.try_to_call_meld(tile, False)

    _assert_tanyao(table.player)

    discard, _ = table.player.discard_tile(tile_to_discard)
    assert tiles_to_string([discard]) == "2m"


def test_we_dont_need_to_discard_terminals_from_closed_hand():
    table = _make_table()
    tiles = string_to_136_array(man="22234", sou="13588", pin="558")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="5")
    table.player.draw_tile(tile)
    tile_to_discard, _ = table.player.discard_tile()

    # our hand is closed, let's keep terminal for now
    assert tiles_to_string([tile_to_discard]) == "8p"


def test_dont_open_tanyao_with_two_non_central_doras():
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="8"))

    tiles = string_to_136_array(man="22234", sou="6888", pin="5599")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="5")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is None


def test_dont_open_tanyao_with_three_not_isolated_terminals():
    table = _make_table()
    tiles = string_to_136_array(man="22256", sou="2799", pin="5579")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(pin="5")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is None


def test_dont_open_tanyao_with_two_not_isolated_terminals_one_shanten():
    table = _make_table()
    tiles = string_to_136_array(man="22234", sou="379", pin="55579")
    table.player.init_hand(tiles)

    tile = string_to_136_tile(man="5")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is None


def test_dont_count_terminal_tiles_in_ukeire():
    table = _make_table()
    # for closed hand let's chose tile with best ukeire
    tiles = string_to_136_array(man="234578", sou="235", pin="2246")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(pin="5"))
    discard, _ = table.player.discard_tile()
    assert (
        tiles_to_string([discard]) == "5m" or tiles_to_string([discard]) == "2m" or tiles_to_string([discard]) == "5s"
    )

    # but with opened hand we don't need to count not suitable tiles as ukeire
    tiles = string_to_136_array(man="234578", sou="235", pin="2246")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))
    table.player.draw_tile(string_to_136_tile(pin="5"))
    discard, _ = table.player.discard_tile()
    assert tiles_to_string([discard]) == "8m"


def test_determine_strategy_when_we_try_to_call_meld():
    table = _make_table()
    table.has_aka_dora = True
    table.player.round_step = 10

    table.add_dora_indicator(string_to_136_tile(sou="5"))
    tiles = string_to_136_array(man="66678", sou="6888", pin="5588")
    table.player.init_hand(tiles)

    # with this red five we will have 2 dora in the hand
    # and in that case we can open our hand
    meld, _ = table.player.try_to_call_meld(FIVE_RED_PIN, False)
    assert meld is not None

    _assert_tanyao(table.player)


def test_correct_discard_agari_no_yaku():
    table = _make_table()
    tiles = string_to_136_array(man="23567", sou="456", pin="22244")
    table.player.init_hand(tiles)

    meld = make_meld(MeldPrint.CHI, man="567")
    table.player.add_called_meld(meld)

    tile = string_to_136_tile(man="1")
    table.player.draw_tile(tile)
    discard, _ = table.player.discard_tile()
    assert tiles_to_string([discard]) == "1m"


# In case we are in temporary furiten, we can't call ron, but can still
# make chi. We assume this chi to be bad, so let's not call it.
def test_dont_meld_agari():
    table = _make_table()
    tiles = string_to_136_array(man="23567", sou="456", pin="22244")
    table.player.init_hand(tiles)

    meld = make_meld(MeldPrint.CHI, man="567")
    table.player.add_called_meld(meld)

    tile = string_to_136_tile(man="4")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def test_dont_open_tanyao_with_good_one_shanten_hand_into_one_shanten():
    table = _make_table()
    table.has_aka_dora = True
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    tiles = string_to_136_array(man="3488", sou="3478", pin="1345") + [FIVE_RED_SOU]  # aka dora
    table.player.init_hand(tiles)
    table.player.round_step = 10

    # tile is not suitable to our strategy
    tile = string_to_136_tile(sou="9")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # after meld we are tempai
    tile = string_to_136_tile(sou="6")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "678s"

    # we have a good one shanten and after meld we are not tempai, abort melding
    tile = FIVE_RED_SOU + 1  # not aka dora
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # we must still take chi when improving from 2-shanten to 1-shanten though
    tiles = string_to_136_array(man="34788", sou="3478", pin="135") + [FIVE_RED_SOU]  # aka dora
    table.player.init_hand(tiles)
    tile = string_to_136_tile(sou="6")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "678s"

    tile = FIVE_RED_SOU + 1  # not aka dora
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # from 2-shanten to 2-shanten, but with clear improvement and dora pon
    tiles = string_to_136_array(man="2257", sou="3456899", pin="68")
    table.player.init_hand(tiles)
    tile = string_to_136_tile(man="2")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is not None
    assert tiles_to_string(meld.tiles) == "222m"


def test_kuikae_simple():
    # case 1: simple chi
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    # but with opened hand we don't need to count not suitable tiles as ukeire
    tiles = string_to_136_array(man="234678", sou="135", pin="3335")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))

    tile = string_to_136_tile(sou="4")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # case 2: kuikae
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    # but with opened hand we don't need to count not suitable tiles as ukeire
    tiles = string_to_136_array(man="234678", sou="123", pin="3335")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))

    tile = string_to_136_tile(sou="4")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    # case 3: no kuikae can be applie to pon
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    # but with opened hand we don't need to count not suitable tiles as ukeire
    tiles = string_to_136_array(man="234678", sou="144", pin="3335")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))

    tile = string_to_136_tile(sou="4")
    meld, _ = table.player.try_to_call_meld(tile, False)
    assert meld is not None

    # case 4: no false kuikae
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    # but with opened hand we don't need to count not suitable tiles as ukeire
    tiles = string_to_136_array(man="234678", sou="237", pin="3335")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))

    tile = string_to_136_tile(sou="4")
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None


def test_kuikae_advanced():
    # case 0: sanity check
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    tiles = string_to_136_array(man="234", sou="23456", pin="33359")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))
    # just force tanyao for the test
    table.player.ai.current_strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)
    _assert_tanyao(table.player)

    tile = string_to_136_array(sou="4444")[1]
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # case 1: allowed chi
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    tiles = string_to_136_array(man="234", sou="123456", pin="3335")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))
    # just force tanyao for the test
    table.player.ai.current_strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)
    _assert_tanyao(table.player)

    tile = string_to_136_array(sou="4444")[1]
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # case 2: another allowed chi
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    tiles = string_to_136_array(man="234", sou="123345", pin="3335")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))
    # just force tanyao for the test
    table.player.ai.current_strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)
    _assert_tanyao(table.player)

    tile = string_to_136_array(sou="4444")[1]
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # case 3: another allowed chi
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    tiles = string_to_136_array(man="234", sou="12345", pin="33355")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))
    # just force tanyao for the test
    table.player.ai.current_strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)
    _assert_tanyao(table.player)

    tile = string_to_136_array(sou="4444")[1]
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is not None

    # case 4: useless chi, don't do that
    table = _make_table()
    table.add_dora_indicator(string_to_136_tile(pin="2"))
    tiles = string_to_136_array(man="234", sou="234567", pin="3335")
    table.player.init_hand(tiles)
    table.player.add_called_meld(make_meld(MeldPrint.CHI, man="234"))
    # just force tanyao for the test
    table.player.ai.current_strategy = TanyaoStrategy(BaseStrategy.TANYAO, table.player)
    _assert_tanyao(table.player)

    tile = string_to_136_array(sou="2222")[2]
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    tile = string_to_136_array(sou="5555")[2]
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None

    tile = string_to_136_array(sou="8888")[2]
    meld, _ = table.player.try_to_call_meld(tile, True)
    assert meld is None


def _make_table():
    table = Table()
    table.has_open_tanyao = True

    # add doras so we are sure to go for tanyao
    table.add_dora_indicator(string_to_136_tile(sou="1"))
    table.add_dora_indicator(string_to_136_tile(man="1"))
    table.add_dora_indicator(string_to_136_tile(pin="1"))

    return table


def _assert_tanyao(player):
    assert player.ai.current_strategy is not None
    assert player.ai.current_strategy.type == BaseStrategy.TANYAO
