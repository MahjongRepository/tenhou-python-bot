from mahjong.player import Player


class Table(object):
    players = []

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

    def init_round(self, round_number, count_of_honba_sticks, count_of_riichi_sticks, dora, dealer, scores):
        self.round_number = round_number
        self.count_of_honba_sticks = count_of_honba_sticks
        self.count_of_riichi_sticks = count_of_riichi_sticks
        self.dora = dora

        self._init_players()
        self.get_player(dealer).is_dealer = True

        self.set_players_scores(scores)

    def init_main_player_hand(self, tiles):
        self.get_main_player().init_hand(tiles)

    def add_open_set(self, meld):
        self.get_player(meld.who).add_open_set(meld)

    def set_players_scores(self, scores, uma=None):
        for i in range(0, len(scores)):
            self.get_player(i).scores = scores[i]

            if uma:
                self.get_player(i).uma = uma[i]

        # recalculate player's positions
        temp_players = self.get_players_sorted_by_scores()
        for i in range(0, len(temp_players)):
            temp_player = temp_players[i]
            self.get_player(temp_player.seat).position = i + 1

    def set_players_names_and_ranks(self, values):
        for x in range(0, len(values)):
            self.get_player(x).name = values[x]['name']
            self.get_player(x).rank = values[x]['rank']

    def get_player(self, player_seat):
        return self.players[player_seat]

    def get_main_player(self):
        return self.players[0]

    def get_players_sorted_by_scores(self):
        return sorted(self.players, key=lambda x: x.scores, reverse=True)

    def _init_players(self):
        self.players = []

        for seat in range(0, 4):
            player = Player(seat=seat)
            self.players.append(player)
