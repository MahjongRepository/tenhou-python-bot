# -*- coding: utf-8 -*-
import unittest

from reproducer import TenhouLogReproducer, SocketMock
from tenhou.client import TenhouClient
from tenhou.decoder import TenhouDecoder, Meld


class TenhouClientTestCase(unittest.TestCase):

    def setUp(self):
        self.client = None

    def tearDown(self):
        self.client.end_game(False)

    def test_fixed_crash_after_called_kan(self):
        log = """
        Get: <HELO uname="Name" auth="20170415-1111111" />
        Get: <LN/>
        Get: <GO type="137" lobby="0" gpid=""/> <UN n0="1" n1="2" n2="3" n3="4" dan="11,12,13,11" rate="1500,1500,1500,1500" sx="M,M,M,M"/> <TAIKYOKU oya="3" log="123"/>
        Get: <INIT seed="6,2,2,5,0,37" ten="203,96,474,207" oya="1" hai="90,83,14,33,132,119,129,117,26,52,121,134,29"/> <U/>
        Get: <E32/> <V/>
        Get: <F108/> <W/>
        Get: <G55/> <T89/>
        Get: <D52/> <U/>
        Get: <E109/> <V/>
        Get: <F124/> <W/>
        Get: <G92/>
        Get: <T77/>
        Get: <D121/> <U/>
        Get: <E125/> <V/>
        Get: <f123/> <W/>
        Get: <G10/> <T38/>
        Get: <D129/> <U/>
        Get: <e0/> <V/>
        Get: <F130/> <W/>
        Get: <G15/> <T42/>
        Get: <D14/> <U/>
        Get: <E64/>
        Get: <V/>
        Get: <f115/>
        Get: <N who="3" m="44075" />
        Get: <G8/> <T5/>
        Get: <D5/> <U/>
        Get: <E70/>
        Get: <V/>
        Get: <f80/> <W/>
        Get: <g111/> <T68/>
        Get: <D68/> <U/>
        Get: <E113/> <V/>
        Get: <F21/> <W/>
        Get: <G128/> <T78/>
        Get: <D38/> <U/>
        Get: <E82/> <V/>
        Get: <f81/> <W/>
        Get: <g6/> <T116/>
        Get: <D42/>
        Get: <N who="1" m="15915" />
        Get: <E50/> <V/>
        Get: <F3/> <W/>
        Get: <G135 t="1"/>
        Get: <N who="0" m="51755" />
        Get: <D77/> <U/>
        Get: <E103/>
        Get: <V/>
        Get: <f76/> <W/>
        Get: <G118 t="3"/>
        Get: <N who="0" m="30211" /> <T39/>
        """

        self.client = TenhouClient(SocketMock(None, log))
        with self.assertRaises(KeyboardInterrupt) as context:
            self.client.connect()
            self.client.authenticate()
            self.client.start_game()

        # close all threads
        self.client.end_game()

        # end of commands is correct way to end log reproducing
        self.assertTrue('End of commands' in str(context.exception))
