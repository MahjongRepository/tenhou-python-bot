import unittest

from game.replays.tenhou import TenhouReplay
from mahjong.meld import Meld
from utils.tests import TestMixin


class TenhouReplayTestCase(unittest.TestCase, TestMixin):

    def test_encode_called_chi(self):
        # 234p
        meld = self._make_meld(Meld.CHI, [42, 44, 51])
        meld.from_who = 3
        replay = TenhouReplay([])

        result = replay._encode_meld(meld)
        self.assertEqual(result, '27031')

    def test_encode_called_pon(self):
        # 555s
        meld = self._make_meld(Meld.PON, [89, 90, 91])
        meld.from_who = 2
        replay = TenhouReplay([])

        result = replay._encode_meld(meld)
        self.assertEqual(result, '34314')
