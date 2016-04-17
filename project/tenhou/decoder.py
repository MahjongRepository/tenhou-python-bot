# Inspired by https://github.com/NegativeMjark/tenhou-log/
import logging

from bs4 import BeautifulSoup

from mahjong.tile import Tile


logger = logging.getLogger('tenhou')


class TenhouDecoder(object):
    """
    This object will decode the Tenhou format and set all values to the
    hand and table objects. So, basically it is translation Tenhou.net -> Our format.
    """

    table = None
    hand = None

    def __init__(self, table, hand):
        self.table = table
        self.hand = hand

    def decode_initial_values(self, message):
        soup = BeautifulSoup(message, 'html.parser')
        tag = soup.find('init')

        # erase all open sets in the start of round
        self.table.open_melds = []

        tiles = tag.attrs['hai']
        tiles = [int(i) for i in tiles.split(',')]
        self.hand.set_initial_hand(tiles)

        """
        Six element list:
            - Round number,
            - Number of honba sticks,
            - Number of riichi sticks,
            - First dice minus one,
            - Second dice minus one,
            - Dora indicator.
        """

        seed = tag.attrs['seed'].split(',')

        round_number = int(seed[0])
        count_of_honba_sticks = int(seed[1])
        count_of_riichi_sticks = int(seed[2])
        dora = int(seed[5])
        dealer = int(tag.attrs['oya'])

        self.table.init_round(round_number, count_of_honba_sticks, count_of_riichi_sticks, dora, dealer)

        logger.info('Init: {0}'.format(self.table))

    def decode_log_link(self, message):
        soup = BeautifulSoup(message, 'html.parser')
        tag = soup.find('taikyoku')

        oya = int(tag.attrs['oya'])
        oya = (4 - oya) % 4
        log = tag.attrs['log']

        logger.info('http://tenhou.net/0/?log={0}&tw={1}'.format(log, oya))

    def decode_tile(self, message):
        # tenhou format: <t23/>, <e23/>, <f23 t="4"/>, <f23/>, <g23/>
        soup = BeautifulSoup(message, 'html.parser')
        tag = soup.findChildren()[0].name
        tile = tag.replace('t', '').replace('e', '').replace('f', '').replace('g', '')
        return int(tile)

    def decode_meld(self, message):
        soup = BeautifulSoup(message, 'html.parser')
        data = soup.find('n').attrs['m']
        data = int(data)

        meld = Meld()
        meld.from_player = data & 0x3
        meld.who = int(soup.find('n').attrs['who'])

        if data & 0x4:
            meld.decode_chi(data)
        elif data & 0x18:
            meld.decode_pon(data)
        elif data & 0x20:
            meld.decode_nuki(data)
        else:
            meld.decode_kan(data)

        self.table.add_open_set(meld)

        logger.info('Called set: {0}'.format(meld))


class Meld(object):
    CHI = 'chi'
    PON = 'pon'
    KAN = 'kan'
    CHAKAN = 'chakan'
    NUKI = 'nuki'

    from_player = False
    who = None
    tiles = []
    type = None
    called = None

    def __str__(self):
        return 'Who: {0}, Type: {1}, Tiles: {2}'.format(self.who, self.type, self.tiles)

    # for calls in array
    def __repr__(self):
        return self.__str__()

    def decode_chi(self, data):
        self.type = Meld.CHI
        t0, t1, t2 = (data >> 3) & 0x3, (data >> 5) & 0x3, (data >> 7) & 0x3
        base_and_called = data >> 10
        self.called = base_and_called % 3
        base = base_and_called // 3
        base = (base // 7) * 9 + base % 7
        self.tiles = Tile(t0 + 4 * (base + 0)), Tile(t1 + 4 * (base + 1)), Tile(t2 + 4 * (base + 2))

    def decode_pon(self, data):
        t4 = (data >> 5) & 0x3
        t0, t1, t2 = ((1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2))[t4]
        base_and_called = data >> 9
        self.called = base_and_called % 3
        base = base_and_called // 3
        if data & 0x8:
            self.type = Meld.PON
            self.tiles = Tile(t0 + 4 * base), Tile(t1 + 4 * base), Tile(t2 + 4 * base)
        else:
            self.type = Meld.CHAKAN
            self.tiles = Tile(t0 + 4 * base), Tile(t1 + 4 * base), Tile(t2 + 4 * base), Tile(t4 + 4 * base)

    def decode_kan(self, data):
        base_and_called = data >> 8
        if self.from_player:
            self.called = base_and_called % 4
        else:
            self.from_player = False
        base = base_and_called // 4
        self.type = Meld.KAN
        self.tiles = Tile(4 * base), Tile(1 + 4 * base), Tile(2 + 4 * base), Tile(3 + 4 * base)

    def decode_nuki(self, data):
        self.from_player = False
        self.type = Meld.NUKI
        self.tiles = Tile(data >> 8)
