import unittest

from mahjong.hand import PlayerHand
from mahjong.table import Table
from tenhou.client import TenhouClient
from tenhou.decoder import TenhouDecoder, Meld


class TenhouClientTestCase(unittest.TestCase):

    def test_generate_auth_token(self):
        client = TenhouClient(None)

        string = '20160318-54ebe070'
        self.assertEqual('20160318-72b5ba21', client._generate_auth_token(string))

        string = '20160319-5b859bb3'
        self.assertEqual('20160319-9bc528f3', client._generate_auth_token(string))

    def test_draw_tile(self):
        client = TenhouClient(None)
        client._draw_tile('<T23/>')
        self.assertEqual(client.hand.tiles[0], 23)

class TenhouDecoderTestCase(unittest.TestCase):

    def test_parse_initial_hand(self):
        hand = PlayerHand()
        table = Table()

        decoder = TenhouDecoder(table, hand)
        decoder.decode_initial_values('<INIT seed="0,2,3,0,1,126" ten="250,250,250,250" oya="3" hai="30,67,44,21,133,123,87,69,36,34,94,4,128"/>')

        self.assertEqual(len(hand.tiles), 13)
        self.assertTrue(table.get_player(3).is_dealer)
        self.assertEqual(table.dora, 126)
        self.assertEqual(table.count_of_honba_sticks, 2)
        self.assertEqual(table.count_of_riichi_sticks, 3)

    def test_parse_called_pon(self):
        hand = PlayerHand()
        table = Table()

        decoder = TenhouDecoder(table, hand)
        decoder.decode_meld('<N who="3" m="34314" />')

        self.assertEqual(len(table.get_player(3).open_sets), 1)
        self.assertEqual(table.get_player(3).open_sets[0].who, 3)
        self.assertEqual(table.get_player(3).open_sets[0].type, Meld.PON)
        self.assertEqual(table.get_player(3).open_sets[0].tiles, (89, 90, 91))

    def test_parse_called_kan(self):
        hand = PlayerHand()
        table = Table()

        decoder = TenhouDecoder(table, hand)
        decoder.decode_meld('<N who="3" m="13825" />')

        self.assertEqual(len(table.get_player(3).open_sets), 1)
        self.assertEqual(table.get_player(3).open_sets[0].who, 3)
        self.assertEqual(table.get_player(3).open_sets[0].type, Meld.KAN)
        self.assertEqual(table.get_player(3).open_sets[0].tiles, (52, 53, 54, 55))

    def test_parse_called_chakan(self):
        hand = PlayerHand()
        table = Table()

        decoder = TenhouDecoder(table, hand)
        decoder.decode_meld('<N who="3" m="18547" />')

        self.assertEqual(len(table.get_player(3).open_sets), 1)
        self.assertEqual(table.get_player(3).open_sets[0].who, 3)
        self.assertEqual(table.get_player(3).open_sets[0].type, Meld.CHAKAN)
        self.assertEqual(table.get_player(3).open_sets[0].tiles, (48, 49, 50, 51))

    def test_parse_called_chi(self):
        hand = PlayerHand()

        table = Table()

        decoder = TenhouDecoder(table, hand)
        decoder.decode_meld('<N who="3" m="27031" />')

        self.assertEqual(len(table.get_player(3).open_sets), 1)
        self.assertEqual(table.get_player(3).open_sets[0].who, 3)
        self.assertEqual(table.get_player(3).open_sets[0].type, Meld.CHI)
        self.assertEqual(table.get_player(3).open_sets[0].tiles, (42, 44, 51))

    def test_parse_tile(self):
        hand = PlayerHand()
        table = Table()
        decoder = TenhouDecoder(table, hand)

        tile = decoder.decode_tile('<t23/>')
        self.assertEqual(tile, 23)

        tile = decoder.decode_tile('<e24/>')
        self.assertEqual(tile, 24)

        tile = decoder.decode_tile('<f25/>')
        self.assertEqual(tile, 25)

        tile = decoder.decode_tile('<g26/>')
        self.assertEqual(tile, 26)

        tile = decoder.decode_tile('<f23 t="4"/>')
        self.assertEqual(tile, 23)