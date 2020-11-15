from game.bots_battle.replays.tenhou import TenhouReplay
from mahjong.meld import Meld
from utils.test_helpers import make_meld


def test_encode_called_chi():
    meld = make_meld(Meld.CHI, tiles=[26, 29, 35])
    meld.who = 3
    meld.from_who = 2
    meld.called_tile = 29
    replay = TenhouReplay("", [], "")

    result = replay._encode_meld(meld)
    assert result == "19895"

    meld = make_meld(Meld.CHI, tiles=[4, 11, 13])
    meld.who = 1
    meld.from_who = 0
    meld.called_tile = 4
    replay = TenhouReplay("", [], "")

    result = replay._encode_meld(meld)
    assert result == "3303"


def test_encode_called_pon():
    meld = make_meld(Meld.PON, tiles=[104, 105, 107])
    meld.who = 0
    meld.from_who = 1
    meld.called_tile = 105
    replay = TenhouReplay("", [], "")

    result = replay._encode_meld(meld)
    assert result == "40521"

    meld = make_meld(Meld.PON, tiles=[124, 126, 127])
    meld.who = 0
    meld.from_who = 2
    meld.called_tile = 124
    replay = TenhouReplay("", [], "")

    result = replay._encode_meld(meld)
    assert result == "47658"


def test_encode_called_daiminkan():
    meld = make_meld(Meld.KAN, tiles=[100, 101, 102, 103])
    meld.who = 2
    meld.from_who = 3
    meld.called_tile = 103
    replay = TenhouReplay("", [], "")

    result = replay._encode_meld(meld)
    assert result == "26369"


def test_encode_called_shouminkan():
    meld = make_meld(Meld.SHOUMINKAN, tiles=[112, 113, 115, 114])
    meld.who = 2
    meld.from_who = 3
    meld.called_tile = 114
    replay = TenhouReplay("", [], "")

    result = replay._encode_meld(meld)
    assert result == "44113"


def test_encode_called_ankan():
    meld = make_meld(Meld.KAN, tiles=[72, 73, 74, 75])
    meld.who = 2
    meld.from_who = 2
    meld.called_tile = 74
    replay = TenhouReplay("", [], "")

    result = replay._encode_meld(meld)
    assert result == "18944"
