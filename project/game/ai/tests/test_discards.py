from game.ai.discard import DiscardOption
from game.ai.strategies.main import BaseStrategy
from game.ai.strategies.tanyao import TanyaoStrategy
from game.table import Table
from mahjong.constants import CHUN, EAST, FIVE_RED_PIN, FIVE_RED_SOU, HAKU, HATSU, NORTH, SOUTH, WEST
from mahjong.tile import Tile
from utils.decisions_logger import MeldPrint
from utils.test_helpers import make_meld, string_to_136_array, string_to_136_tile, tiles_to_string


def test_discard_tile():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="11134567", pin="159", man="45")
    tile = string_to_136_tile(man="9")
    player.init_hand(tiles)
    player.draw_tile(tile)

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "9m" or tiles_to_string([discarded_tile]) == "9p"
    assert player.ai.shanten == 2

    player.draw_tile(string_to_136_tile(pin="4"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "1p"
    assert player.ai.shanten == 2

    player.draw_tile(string_to_136_tile(pin="3"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "9p" or tiles_to_string([discarded_tile]) == "9m"
    assert player.ai.shanten == 1

    player.draw_tile(string_to_136_tile(man="4"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "5m"
    assert player.ai.shanten == 0


def test_discard_tile_force_tsumogiri():
    table = Table()
    table.has_aka_dora = True
    player = table.player

    tiles = string_to_136_array(sou="11134567", pin="456", man="45")
    # 6p
    tile = 57

    player.init_hand(tiles)
    player.draw_tile(tile)

    discarded_tile, _ = player.discard_tile()
    assert discarded_tile == tile

    # add not red five pin
    tiles = string_to_136_array(sou="11134567", pin="46", man="45") + [53]
    tile = FIVE_RED_PIN

    player.init_hand(tiles)
    player.draw_tile(tile)

    discarded_tile, _ = player.discard_tile()
    # WE DON'T NEED TO DISCARD RED FIVE
    assert discarded_tile != tile


def test_calculate_suit_tiles_value():
    table = Table()
    player = table.player
    table.has_aka_dora = False

    # 0 - 8   man
    # 9 - 17  pin
    # 18 - 26 sou
    results = [
        [0, 110],
        [9, 110],
        [18, 110],
        [1, 120],
        [10, 120],
        [19, 120],
        [2, 140],
        [11, 140],
        [20, 140],
        [3, 150],
        [12, 150],
        [21, 150],
        [4, 130],
        [13, 130],
        [22, 130],
        [5, 150],
        [14, 150],
        [23, 150],
        [6, 140],
        [15, 140],
        [24, 140],
        [7, 120],
        [16, 120],
        [25, 120],
        [8, 110],
        [17, 110],
        [26, 110],
    ]

    for item in results:
        tile = item[0]
        value = item[1]
        assert DiscardOption(player, tile * 4, 0, [], 0).valuation == value
        assert DiscardOption(player, tile * 4 + 1, 0, [], 0).valuation == value
        assert DiscardOption(player, tile * 4 + 2, 0, [], 0).valuation == value
        assert DiscardOption(player, tile * 4 + 3, 0, [], 0).valuation == value


def test_calculate_suit_tiles_value_and_tanyao_hand():
    table = Table()
    player = table.player
    table.has_aka_dora = False
    player.ai.current_strategy = TanyaoStrategy(BaseStrategy.TANYAO, player)

    # 0 - 8   man
    # 9 - 17  pin
    # 18 - 26 sou
    results = [
        [0, 110],
        [9, 110],
        [18, 110],
        [1, 120],
        [10, 120],
        [19, 120],
        [2, 130],
        [11, 130],
        [20, 130],
        [3, 150],
        [12, 150],
        [21, 150],
        [4, 140],
        [13, 140],
        [22, 140],
        [5, 150],
        [14, 150],
        [23, 150],
        [6, 130],
        [15, 130],
        [24, 130],
        [7, 120],
        [16, 120],
        [25, 120],
        [8, 110],
        [17, 110],
        [26, 110],
    ]

    for item in results:
        tile = item[0]
        value = item[1]
        assert DiscardOption(player, tile * 4, 0, [], 0).valuation == value
        assert DiscardOption(player, tile * 4 + 1, 0, [], 0).valuation == value
        assert DiscardOption(player, tile * 4 + 2, 0, [], 0).valuation == value
        assert DiscardOption(player, tile * 4 + 3, 0, [], 0).valuation == value


def test_calculate_honor_tiles_value():
    table = Table()
    player = table.player
    player.dealer_seat = 3
    table.has_aka_dora = False

    # valuable honor, wind of the round
    option = DiscardOption(player, EAST * 4, 0, [], 0)
    assert option.valuation == 120

    # valuable honor, wind of the player
    option = DiscardOption(player, SOUTH * 4, 0, [], 0)
    assert option.valuation == 120

    # not valuable wind
    option = DiscardOption(player, WEST * 4, 0, [], 0)
    assert option.valuation == 100

    # not valuable wind
    option = DiscardOption(player, NORTH * 4, 0, [], 0)
    assert option.valuation == 100

    # valuable dragon
    option = DiscardOption(player, HAKU * 4, 0, [], 0)
    assert option.valuation == 120

    # valuable dragon
    option = DiscardOption(player, HATSU * 4, 0, [], 0)
    assert option.valuation == 120

    # valuable dragon
    option = DiscardOption(player, CHUN * 4, 0, [], 0)
    assert option.valuation == 120

    player.dealer_seat = 0

    # double wind
    option = DiscardOption(player, EAST * 4, 0, [], 0)
    assert option.valuation == 140


def test_calculate_suit_tiles_value_and_dora():
    table = Table()
    table.dora_indicators = [string_to_136_tile(sou="9")]
    player = table.player
    table.has_aka_dora = False

    tile = string_to_136_tile(sou="1")
    option = DiscardOption(player, tile, 0, [], 0)
    assert option.valuation == (DiscardOption.DORA_VALUE + 110)

    # double dora
    table.dora_indicators = [string_to_136_tile(sou="9"), string_to_136_tile(sou="9")]
    tile = string_to_136_tile(sou="1")
    option = DiscardOption(player, tile, 0, [], 0)
    assert option.valuation == ((DiscardOption.DORA_VALUE * 2) + 110)

    # tile close to dora
    table.dora_indicators = [string_to_136_tile(sou="9")]
    tile = string_to_136_tile(sou="2")
    option = DiscardOption(player, tile, 0, [], 0)
    assert option.valuation == (DiscardOption.DORA_FIRST_NEIGHBOUR + 120)

    # tile not far away from dora
    table.dora_indicators = [string_to_136_tile(sou="9")]
    tile = string_to_136_tile(sou="3")
    option = DiscardOption(player, tile, 0, [], 0)
    assert option.valuation == (DiscardOption.DORA_SECOND_NEIGHBOUR + 140)

    # tile from other suit
    table.dora_indicators = [string_to_136_tile(sou="9")]
    tile = string_to_136_tile(man="3")
    option = DiscardOption(player, tile, 0, [], 0)
    assert option.valuation == 140


def test_discard_not_valuable_honor_first():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="123456", pin="123455", man="9", honors="2")
    player.init_hand(tiles)

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "2z"


def test_slide_set_to_keep_dora_in_hand():
    table = Table()
    table.dora_indicators = [string_to_136_tile(pin="9")]
    player = table.player

    tiles = string_to_136_array(sou="123456", pin="23478", man="99")
    tile = string_to_136_tile(pin="1")
    player.init_hand(tiles)
    player.draw_tile(tile)

    # 2p is a dora, we had to keep it
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "4p"


def test_keep_aka_dora_in_hand():
    table = Table()
    table.dora_indicators = [string_to_136_tile(pin="1")]
    table.has_aka_dora = True
    player = table.player

    tiles = string_to_136_array(sou="12346", pin="34578", man="99")
    # five sou, we can't get it from string (because from string it is always aka dora)
    tiles += [89]
    player.init_hand(tiles)
    player.draw_tile(FIVE_RED_SOU)

    # we had to keep red five and discard just 5s
    discarded_tile, _ = player.discard_tile()
    assert discarded_tile != FIVE_RED_SOU


def test_dont_keep_honor_with_small_number_of_shanten():
    table = Table()
    player = table.player

    tiles = string_to_136_array(sou="11445", pin="55699", man="246")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(honors="7"))

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "7z"


def test_prefer_valuable_tiles_with_almost_same_ukeire():
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(sou="4"))

    tiles = string_to_136_array(sou="1366", pin="123456", man="345")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(sou="5"))

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "1s"


def test_discard_less_valuable_isolated_tile_first():
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(sou="4"))

    tiles = string_to_136_array(sou="2456", pin="129", man="234458")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(sou="7"))

    discarded_tile, _ = player.discard_tile()
    # we have a choice what to discard: 9p or 8m
    # 9p is less valuable
    assert tiles_to_string([discarded_tile]) == "9p"

    table.dora_indicators.append(string_to_136_tile(pin="8"))
    tiles = string_to_136_array(sou="2456", pin="129", man="234458")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(sou="7"))
    discarded_tile, _ = player.discard_tile()
    # but if 9p is dora
    # let's discard 8m instead
    assert tiles_to_string([discarded_tile]) == "8m"


def test_discard_tile_with_max_ukeire_second_level():
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(sou="4"))

    tiles = string_to_136_array(sou="11367", pin="45", man="344778")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(pin="6"))

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "3s"


# There was a bug with count of live tiles that are used in melds,
# hence this test
def test_choose_best_option_with_melds():
    table = Table()
    player = table.player
    table.has_aka_dora = False

    tiles = string_to_136_array(sou="245666789", honors="2266")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, sou="666")
    player.add_called_meld(meld)
    meld = make_meld(MeldPrint.CHI, sou="789")
    player.add_called_meld(meld)

    player.draw_tile(string_to_136_tile(sou="5"))

    discarded_tile, _ = player.discard_tile()
    # we should discard best ukeire option here - 2s
    assert tiles_to_string([discarded_tile]) == "2s"


def test_choose_best_wait_with_melds():
    table = Table()
    player = table.player
    table.has_aka_dora = False

    tiles = string_to_136_array(sou="3499222555123")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, sou="222")
    table.add_called_meld(0, meld)
    # 123s, we can't automatically chose correct index for fourth 2s
    meld = make_meld(MeldPrint.CHI, tiles=[72, 79, 80])
    table.add_called_meld(0, meld)
    meld = make_meld(MeldPrint.PON, sou="555")
    table.add_called_meld(0, meld)

    player.draw_tile(string_to_136_tile(sou="4"))
    discarded_tile, _ = player.discard_tile()
    # double-pairs wait becomes better, because it has 4 tiles to wait for
    # against just 1 in ryanmen
    assert tiles_to_string([discarded_tile]) == "3s"


def test_discard_tile_with_better_wait_in_iishanten():
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(sou="4"))

    tiles = string_to_136_array(man="123567", pin="113788", sou="99")
    player.init_hand(tiles)

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "8p"


def test_discard_tile_and_wrong_tiles_valuation():
    """
    Bot wanted to discard 5m from the first hand,
    because valuation for 2p was miscalculated (too high)

    Same issue with wrong valuation was with second hand
    """
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(honors="2"))

    tiles = string_to_136_array(man="5", pin="256678", sou="2333467")
    player.init_hand(tiles)

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "2p"

    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(man="5"))

    tiles = string_to_136_array(man="45667", pin="34677", sou="38", honors="22")
    player.init_hand(tiles)

    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "8s"


def test_choose_correct_wait_finished_yaku():
    table = Table()
    player = table.player
    player.round_step = 2

    tiles = string_to_136_array(man="23478", sou="23488", pin="235")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(pin="4"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "5p"

    tiles = string_to_136_array(man="34578", sou="34588", pin="235")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(pin="4"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "2p"

    tiles = string_to_136_array(man="34578", sou="34588", pin="235")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(pin="4"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "2p"

    tiles = string_to_136_array(man="3457", sou="233445588")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(man="8"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "2s"

    tiles = string_to_136_array(man="3457", sou="223344588")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(man="8"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "5s"


def test_choose_correct_wait_yaku_versus_dora():
    table = Table()
    player = table.player
    player.round_step = 2

    table.add_dora_indicator(string_to_136_tile(pin="4"))

    tiles = string_to_136_array(man="23478", sou="23488", pin="235")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(pin="4"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "5p"

    table = Table()
    player = table.player
    player.round_step = 2

    table.add_dora_indicator(string_to_136_tile(pin="1"))

    tiles = string_to_136_array(man="34578", sou="34588", pin="235")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(pin="4"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "2p"


def test_choose_correct_wait_yaku_potentially():
    table = Table()
    player = table.player
    player.round_step = 2

    tiles = string_to_136_array(man="1134578", sou="567788")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(man="9"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "5s"

    tiles = string_to_136_array(man="1134578", sou="556678")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(man="9"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "8s"


def test_choose_better_tanki_honor():
    table = Table()
    player = table.player
    player.round_step = 2
    player.dealer_seat = 3

    table.add_dora_indicator(string_to_136_tile(man="8"))

    tiles = string_to_136_array(man="11447799", sou="556", honors="45")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(honors="4"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "6s"

    tiles = string_to_136_array(man="11447799", sou="556", honors="45")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(honors="5"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "6s"

    tiles = string_to_136_array(man="11447799", sou="556", honors="45")
    player.init_hand(tiles)
    player.draw_tile(string_to_136_tile(sou="6"))
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == "5z"


def test_choose_tanki_with_kabe():
    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="119", pin="224477", man="5669"),
        [string_to_136_tile(sou="8")],
        string_to_136_tile(man="5"),
        "9m",
    )

    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="119", pin="224477", man="5669"),
        [string_to_136_tile(man="8")],
        string_to_136_tile(man="5"),
        "9s",
    )

    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="118", pin="224477", man="5668"),
        [string_to_136_tile(sou="7")],
        string_to_136_tile(man="5"),
        "8m",
    )

    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="118", pin="224477", man="5668"),
        [string_to_136_tile(man="7")],
        string_to_136_tile(man="5"),
        "8s",
    )

    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="117", pin="224477", man="1157"),
        [string_to_136_tile(sou="6"), string_to_136_tile(sou="9")],
        string_to_136_tile(man="5"),
        "7m",
    )

    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="117", pin="224477", man="1157"),
        [string_to_136_tile(man="6"), string_to_136_tile(man="9")],
        string_to_136_tile(man="5"),
        "7s",
    )

    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="116", pin="224477", man="1126"),
        [string_to_136_tile(sou="5"), string_to_136_tile(sou="7")],
        string_to_136_tile(man="2"),
        "6m",
    )

    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="116", pin="224477", man="1126"),
        [string_to_136_tile(man="5"), string_to_136_tile(man="7")],
        string_to_136_tile(man="2"),
        "6s",
    )

    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="115", pin="224477", man="1125"),
        [string_to_136_tile(sou="4"), string_to_136_tile(sou="6")],
        string_to_136_tile(man="2"),
        "5m",
    )

    _choose_tanki_with_kabe_helper(
        string_to_136_array(sou="115", pin="224477", man="1125"),
        [string_to_136_tile(man="4"), string_to_136_tile(man="6")],
        string_to_136_tile(man="2"),
        "5s",
    )


def test_choose_tanki_with_suji():
    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="19", pin="99", honors="2"),
        [string_to_136_tile(sou="6")],
        string_to_136_tile(honors="2"),
        "1s",
    )

    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="19", pin="99", honors="2"),
        [string_to_136_tile(sou="4")],
        string_to_136_tile(honors="2"),
        "9s",
    )

    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="2", pin="299", honors="2"),
        [string_to_136_tile(sou="5")],
        string_to_136_tile(honors="2"),
        "2p",
    )

    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="2", pin="299", honors="2"),
        [string_to_136_tile(pin="5")],
        string_to_136_tile(honors="2"),
        "2s",
    )

    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="3", pin="399", honors="2"),
        [string_to_136_tile(sou="6")],
        string_to_136_tile(honors="2"),
        "3p",
    )

    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="3", pin="399", honors="2"),
        [string_to_136_tile(pin="6")],
        string_to_136_tile(honors="2"),
        "3s",
    )

    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="4", pin="499", honors="2"),
        [string_to_136_tile(sou="1"), string_to_136_tile(sou="7")],
        string_to_136_tile(honors="2"),
        "4p",
    )

    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="4", pin="499", honors="2"),
        [string_to_136_tile(pin="1"), string_to_136_tile(pin="7")],
        string_to_136_tile(honors="2"),
        "4s",
    )

    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="5", pin="599", honors="2"),
        [string_to_136_tile(sou="2"), string_to_136_tile(sou="8")],
        string_to_136_tile(honors="2"),
        "5p",
    )

    _choose_tanki_with_suji_helper(
        string_to_136_array(man="22336688", sou="5", pin="599", honors="2"),
        [string_to_136_tile(pin="2"), string_to_136_tile(pin="8")],
        string_to_136_tile(honors="2"),
        "5s",
    )


def test_avoid_furiten():
    _avoid_furiten_helper(
        string_to_136_array(man="22336688", pin="99", honors="267"),
        string_to_136_tile(honors="6"),
        string_to_136_tile(honors="7"),
        string_to_136_tile(honors="2"),
        "6z",
    )

    _avoid_furiten_helper(
        string_to_136_array(man="22336688", pin="99", honors="267"),
        string_to_136_tile(honors="7"),
        string_to_136_tile(honors="6"),
        string_to_136_tile(honors="2"),
        "7z",
    )


def test_choose_furiten_over_karaten():
    _choose_furiten_over_karaten_helper(
        string_to_136_array(man="22336688", pin="99", honors="267"),
        string_to_136_tile(honors="6"),
        string_to_136_tile(honors="7"),
        string_to_136_tile(honors="2"),
        "7z",
    )

    _choose_furiten_over_karaten_helper(
        string_to_136_array(man="22336688", pin="99", honors="267"),
        string_to_136_tile(honors="7"),
        string_to_136_tile(honors="6"),
        string_to_136_tile(honors="2"),
        "6z",
    )


def test_discard_tile_based_on_second_level_ukeire_and_cost():
    table = Table()
    player = table.player

    table.add_dora_indicator(string_to_136_tile(man="2"))
    table.add_discarded_tile(1, string_to_136_tile(man="2"), False)

    tiles = string_to_136_array(man="34678", pin="2356", sou="4467")
    tile = string_to_136_tile(sou="8")

    player.init_hand(tiles)
    player.draw_tile(tile)

    discarded_tile, _ = player.discard_tile()
    discard_correct = tiles_to_string([discarded_tile]) == "2p" or tiles_to_string([discarded_tile]) == "3p"
    assert discard_correct is True


def test_calculate_second_level_ukeire():
    """
    There was a bug with 2356 form and second level ukeire
    """
    table = Table()
    player = table.player

    table.add_dora_indicator(string_to_136_tile(man="2"))
    table.add_discarded_tile(1, string_to_136_tile(man="2"), False)
    table.add_discarded_tile(1, string_to_136_tile(pin="3"), False)
    table.add_discarded_tile(1, string_to_136_tile(pin="3"), False)

    tiles = string_to_136_array(man="34678", pin="2356", sou="4467")
    tile = string_to_136_tile(sou="8")

    player.init_hand(tiles)
    player.draw_tile(tile)

    discard_options, _ = player.ai.hand_builder.find_discard_options()

    tile = string_to_136_tile(man="4")
    discard_option = [x for x in discard_options if x.tile_to_discard_34 == tile // 4][0]
    player.ai.hand_builder.calculate_second_level_ukeire(discard_option)
    assert discard_option.ukeire_second == 108

    tile = string_to_136_tile(man="3")
    discard_option = [x for x in discard_options if x.tile_to_discard_34 == tile // 4][0]
    player.ai.hand_builder.calculate_second_level_ukeire(discard_option)
    assert discard_option.ukeire_second == 108

    tile = string_to_136_tile(pin="2")
    discard_option = [x for x in discard_options if x.tile_to_discard_34 == tile // 4][0]
    player.ai.hand_builder.calculate_second_level_ukeire(discard_option)
    assert discard_option.ukeire_second == 96

    tile = string_to_136_tile(pin="3")
    discard_option = [x for x in discard_options if x.tile_to_discard_34 == tile // 4][0]
    player.ai.hand_builder.calculate_second_level_ukeire(discard_option)
    assert discard_option.ukeire_second == 96

    tile = string_to_136_tile(pin="5")
    discard_option = [x for x in discard_options if x.tile_to_discard_34 == tile // 4][0]
    player.ai.hand_builder.calculate_second_level_ukeire(discard_option)
    assert discard_option.ukeire_second == 96

    tile = string_to_136_tile(pin="6")
    discard_option = [x for x in discard_options if x.tile_to_discard_34 == tile // 4][0]
    player.ai.hand_builder.calculate_second_level_ukeire(discard_option)
    assert discard_option.ukeire_second == 96


def test_choose_1_shanten_with_cost_possibility_draw():
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(sou="4"))

    tiles = string_to_136_array(man="557", pin="468", sou="55577", honors="66")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, sou="555")
    player.add_called_meld(meld)

    tile = string_to_136_tile(sou="7")
    player.draw_tile(tile)
    discarded_tile, _ = player.discard_tile()
    assert player.ai.current_strategy is not None
    assert player.ai.current_strategy.type == BaseStrategy.YAKUHAI
    assert tiles_to_string([discarded_tile]) == "7m"


def test_choose_1_shanten_with_cost_possibility_meld():
    table = Table()
    player = table.player
    table.add_dora_indicator(string_to_136_tile(sou="4"))

    tiles = string_to_136_array(man="557", pin="468", sou="55577", honors="66")
    player.init_hand(tiles)

    meld = make_meld(MeldPrint.PON, sou="555")
    player.add_called_meld(meld)

    tile = string_to_136_tile(sou="7")
    meld, discard_option = player.try_to_call_meld(tile, False)
    assert meld is not None
    assert meld.type == MeldPrint.PON
    assert tiles_to_string(meld.tiles) == "777s"

    assert player.ai.current_strategy is not None
    assert player.ai.current_strategy.type == BaseStrategy.YAKUHAI

    discarded_tile = discard_option.tile_to_discard_136

    assert tiles_to_string([discarded_tile]) == "7m"


def _choose_tanki_with_kabe_helper(tiles, kabe_tiles, tile_to_draw, tile_to_discard_str):
    table = Table()
    player = table.player
    player.round_step = 2
    player.dealer_seat = 3

    for tile in kabe_tiles:
        for _ in range(0, 4):
            table.add_discarded_tile(1, tile, False)

    player.init_hand(tiles)
    player.draw_tile(tile_to_draw)
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == tile_to_discard_str


def _choose_tanki_with_suji_helper(tiles, suji_tiles, tile_to_draw, tile_to_discard_str):
    table = Table()
    player = table.player
    player.round_step = 2
    player.dealer_seat = 3

    player.init_hand(tiles)

    for tile in suji_tiles:
        player.add_discarded_tile(Tile(tile, True))

    player.draw_tile(tile_to_draw)
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == tile_to_discard_str


def _avoid_furiten_helper(tiles, furiten_tile, other_tile, tile_to_draw, tile_to_discard_str):
    table = Table()
    player = table.player
    player.round_step = 2
    player.dealer_seat = 3

    player.init_hand(tiles)

    player.add_discarded_tile(Tile(furiten_tile, True))

    for _ in range(0, 2):
        table.add_discarded_tile(1, other_tile, False)

    player.draw_tile(tile_to_draw)
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == tile_to_discard_str


def _choose_furiten_over_karaten_helper(tiles, furiten_tile, karaten_tile, tile_to_draw, tile_to_discard_str):
    table = Table()
    player = table.player
    player.round_step = 2
    player.dealer_seat = 3

    player.init_hand(tiles)

    player.add_discarded_tile(Tile(furiten_tile, True))

    for _ in range(0, 3):
        table.add_discarded_tile(1, karaten_tile, False)

    player.draw_tile(tile_to_draw)
    discarded_tile, _ = player.discard_tile()
    assert tiles_to_string([discarded_tile]) == tile_to_discard_str
