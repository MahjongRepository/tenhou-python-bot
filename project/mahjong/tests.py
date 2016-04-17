import unittest

from mahjong.table import Table
from tenhou.decoder import Meld


class TableTestCase(unittest.TestCase):

    def test_new_table_and_players_initialization(self):
        table = Table()

        self.assertEqual(len(table.players), 4)
        self.assertTrue(all([i.is_dealer == False for i in table.players.values()]))
        self.assertTrue(all([len(i.discards) == 0 for i in table.players.values()]))
        self.assertTrue(all([len(i.open_sets) == 0 for i in table.players.values()]))

        self.assertEqual(table.get_player(0).number, 0)
        self.assertEqual(table.get_player(1).number, 1)
        self.assertEqual(table.get_player(2).number, 2)
        self.assertEqual(table.get_player(3).number, 3)

    def test_open_set(self):
        table = Table()

        meld = Meld()
        meld.who = 2
        meld.type = Meld.PON

        table.add_open_set(meld)

        self.assertEqual(len(table.get_player(2).open_sets), 1)