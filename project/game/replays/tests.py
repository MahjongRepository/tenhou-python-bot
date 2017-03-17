import unittest

from game.replays.tenhou import TenhouReplay
from mahjong.meld import Meld
from utils.tests import TestMixin


class TenhouReplayTestCase(unittest.TestCase, TestMixin):

    def test_encode_called_chi(self):
        meld = self._make_meld(Meld.CHI, [26, 29, 35])
        meld.who = 3
        meld.from_who = 2
        meld.called_tile = 29
        replay = TenhouReplay('', [])

        result = replay._encode_meld(meld)
        self.assertEqual(result, '19895')

        meld = self._make_meld(Meld.CHI, [4, 11, 13])
        meld.who = 1
        meld.from_who = 0
        meld.called_tile = 4
        replay = TenhouReplay('', [])

        result = replay._encode_meld(meld)
        self.assertEqual(result, '3303')

    def test_encode_called_pon(self):
        meld = self._make_meld(Meld.PON, [104, 105, 107])
        meld.who = 0
        meld.from_who = 1
        meld.called_tile = 105
        replay = TenhouReplay('', [])

        result = replay._encode_meld(meld)
        self.assertEqual(result, '40521')

        meld = self._make_meld(Meld.PON, [124, 126, 127])
        meld.who = 0
        meld.from_who = 2
        meld.called_tile = 124
        replay = TenhouReplay('', [])

        result = replay._encode_meld(meld)
        self.assertEqual(result, '47658')
