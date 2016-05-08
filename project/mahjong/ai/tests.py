import unittest

from mahjong.ai.first import FirstAI
from mahjong.player import Player
from mahjong.table import Table


class FirstAITestCase(unittest.TestCase):

    def test_calculate_outs(self):
        table = Table()
        player = Player(0, table)
        ai = FirstAI(player)

        player.init_hand([30, 67, 44, 21, 133, 123, 87, 69, 36, 34, 94, 4, 128])
        player.draw_tile(40)

        shanten = ai.calculate_outs()

        self.assertEqual(shanten, 10)
