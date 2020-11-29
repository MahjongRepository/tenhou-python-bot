from game.table import Table
from mahjong.tile import Tile
from utils.test_helpers import string_to_136_array, string_to_136_tile


def test_dont_call_riichi_with_yaku_and_central_tanki_wait():
    table = _make_table()

    tiles = string_to_136_array(sou="234567", pin="234567", man="4")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(man="5"))
    _, with_riichi = table.player.discard_tile()

    assert with_riichi is False


def test_dont_call_riichi_expensive_damaten_with_yaku():
    table = _make_table(
        dora_indicators=[
            string_to_136_tile(man="7"),
            string_to_136_tile(man="5"),
            string_to_136_tile(sou="1"),
        ]
    )

    # tanyao pinfu sanshoku dora 4 - this is damaten baiman, let's not riichi it
    tiles = string_to_136_array(man="67888", sou="678", pin="34678")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is False

    # let's test lots of doras hand, tanyao dora 8, also damaten baiman
    tiles = string_to_136_array(man="666888", sou="22", pin="34678")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is False

    # chuuren
    tiles = string_to_136_array(man="1112345678999")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is False


def test_riichi_expensive_hand_without_yaku():
    table = _make_table(
        dora_indicators=[
            string_to_136_tile(man="1"),
            string_to_136_tile(sou="1"),
            string_to_136_tile(pin="1"),
        ]
    )

    tiles = string_to_136_array(man="222", sou="22278", pin="22789")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is True


def test_riichi_tanki_honor_without_yaku():
    table = _make_table(dora_indicators=[string_to_136_tile(man="2"), string_to_136_tile(sou="6")])

    tiles = string_to_136_array(man="345678", sou="789", pin="123", honors="2")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is True


def test_riichi_tanki_honor_chiitoitsu():
    table = _make_table()

    tiles = string_to_136_array(man="22336688", sou="99", pin="99", honors="2")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is True


def test_always_call_daburi():
    table = _make_table()
    table.player.round_step = 0

    tiles = string_to_136_array(sou="234567", pin="234567", man="4")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(man="5"))
    _, with_riichi = table.player.discard_tile()

    assert with_riichi is True


def test_dont_call_karaten_tanki_riichi():
    table = _make_table()

    tiles = string_to_136_array(man="22336688", sou="99", pin="99", honors="2")
    table.player.init_hand(tiles)

    for _ in range(0, 3):
        table.add_discarded_tile(1, string_to_136_tile(honors="2"), False)
        table.add_discarded_tile(1, string_to_136_tile(honors="3"), False)

    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is False


def test_dont_call_karaten_ryanmen_riichi():
    table = _make_table(
        dora_indicators=[
            string_to_136_tile(man="1"),
            string_to_136_tile(sou="1"),
            string_to_136_tile(pin="1"),
        ]
    )

    tiles = string_to_136_array(man="222", sou="22278", pin="22789")
    table.player.init_hand(tiles)

    for _ in range(0, 4):
        table.add_discarded_tile(1, string_to_136_tile(sou="6"), False)
        table.add_discarded_tile(1, string_to_136_tile(sou="9"), False)

    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is False


def test_call_riichi_penchan_with_suji():
    table = _make_table(
        dora_indicators=[
            string_to_136_tile(pin="1"),
        ]
    )

    tiles = string_to_136_array(sou="11223", pin="234567", man="66")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(sou="6"))
    _, with_riichi = table.player.discard_tile()

    assert with_riichi is True


def test_call_riichi_tanki_with_kabe():
    table = _make_table(
        dora_indicators=[
            string_to_136_tile(pin="1"),
        ]
    )

    for _ in range(0, 3):
        table.add_discarded_tile(1, string_to_136_tile(honors="1"), False)

    for _ in range(0, 4):
        table.add_discarded_tile(1, string_to_136_tile(sou="8"), False)

    tiles = string_to_136_array(sou="1119", pin="234567", man="666")
    table.player.init_hand(tiles)
    table.player.draw_tile(string_to_136_tile(honors="1"))
    _, with_riichi = table.player.discard_tile()

    assert with_riichi is True


def test_call_riichi_chiitoitsu_with_suji():
    table = _make_table(
        dora_indicators=[
            string_to_136_tile(man="1"),
        ]
    )

    for _ in range(0, 3):
        table.add_discarded_tile(1, string_to_136_tile(honors="3"), False)

    tiles = string_to_136_array(man="22336688", sou="9", pin="99", honors="22")
    table.player.init_hand(tiles)
    table.player.add_discarded_tile(Tile(string_to_136_tile(sou="6"), True))

    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is True


def test_dont_call_riichi_chiitoitsu_bad_wait():
    table = _make_table(
        dora_indicators=[
            string_to_136_tile(man="1"),
        ]
    )

    for _ in range(0, 3):
        table.add_discarded_tile(1, string_to_136_tile(honors="3"), False)

    tiles = string_to_136_array(man="22336688", sou="4", pin="99", honors="22")
    table.player.init_hand(tiles)

    table.player.draw_tile(string_to_136_tile(honors="3"))
    _, with_riichi = table.player.discard_tile()
    assert with_riichi is False


def _make_table(dora_indicators=None):
    table = Table()
    table.count_of_remaining_tiles = 60
    table.player.scores = 25000

    # with that we don't have daburi anymore
    table.player.round_step = 1

    if dora_indicators:
        for x in dora_indicators:
            table.add_dora_indicator(x)

    return table
