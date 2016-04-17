from mahjong.hand import Player


class Table(object):
    players = {}

    dora = None

    round_number = 0
    count_of_riichi_sticks = 0
    count_of_honba_sticks = 0

    def __init__(self):
        self._init_players()

    def __str__(self):
        return 'Round: {0}, Dora: {1}, Riichi sticks: {2}, Honba sticks: {3}'.format(self.round_number,
                                                                                     self.dora,
                                                                                     self.count_of_riichi_sticks,
                                                                                     self.count_of_honba_sticks)

    def init_round(self, round_number, count_of_honba_sticks, count_of_riichi_sticks, dora, dealer):
        self.round_number = round_number
        self.count_of_honba_sticks = count_of_honba_sticks
        self.count_of_riichi_sticks = count_of_riichi_sticks
        self.dora = dora

        self._init_players()
        self.get_player(dealer).is_dealer = True

    def add_open_set(self, meld):
        self.get_player(meld.who).add_open_set(meld)

    def get_player(self, position):
        return self.players[position]

    def _init_players(self):
        self.players = {}

        for number in range(0, 4):
            player = Player(number=number)
            self.players[number] = player