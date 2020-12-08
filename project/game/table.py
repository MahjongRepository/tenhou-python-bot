from game.player import EnemyPlayer, Player
from mahjong.constants import EAST, NORTH, SOUTH, WEST
from mahjong.tile import Tile, TilesConverter
from mahjong.utils import plus_dora
from utils.decisions_logger import MeldPrint
from utils.general import is_sangenpai


class Table:
    # our bot
    player = None
    # main bot + all other players
    players = None

    dora_indicators = None

    dealer_seat = 0
    round_number = -1
    round_wind_number = 0
    count_of_riichi_sticks = 0
    count_of_honba_sticks = 0

    count_of_remaining_tiles = 0
    count_of_players = 4

    meld_was_called = False

    # array of tiles in 34 format
    revealed_tiles = None
    revealed_tiles_136 = None

    # bot is playing mainly with ari-ari rules, so we can have them as default
    has_open_tanyao = True
    has_aka_dora = True

    def __init__(self, bot_config=None):
        self._init_players(bot_config)
        self.dora_indicators = []
        self.revealed_tiles = [0] * 34
        self.revealed_tiles_136 = []

    def __str__(self):
        dora_string = TilesConverter.to_one_line_string(
            self.dora_indicators, print_aka_dora=self.player.table.has_aka_dora
        )

        return "Wind: {}, Honba: {}, Dora Indicators: {}".format(
            self.round_wind_number, self.count_of_honba_sticks, dora_string
        )

    def init_round(
        self, round_wind_number, count_of_honba_sticks, count_of_riichi_sticks, dora_indicator, dealer_seat, scores
    ):

        # we need it to properly display log for each round
        self.round_number += 1

        self.meld_was_called = False
        self.dealer_seat = dealer_seat
        self.round_wind_number = round_wind_number
        self.count_of_honba_sticks = count_of_honba_sticks
        self.count_of_riichi_sticks = count_of_riichi_sticks

        self.revealed_tiles = [0] * 34
        self.revealed_tiles_136 = []

        self.dora_indicators = []
        self.add_dora_indicator(dora_indicator)

        # erase players state
        for player in self.players:
            player.erase_state()
            player.dealer_seat = dealer_seat
        self.set_players_scores(scores)

        # 136 - total count of tiles
        # 14 - tiles in dead wall
        # 13 - tiles in each player hand
        self.count_of_remaining_tiles = 136 - 14 - self.count_of_players * 13

        if round_wind_number == 0 and count_of_honba_sticks == 0:
            i = 0
            seats = [0, 1, 2, 3]
            for player in self.players:
                player.first_seat = seats[i - dealer_seat]
                i += 1

    def erase_state(self):
        self.dora_indicators = []
        self.revealed_tiles = [0] * 34
        self.revealed_tiles_136 = []

    def add_called_meld(self, player_seat, meld):
        self.meld_was_called = True

        # if meld was called from the other player, then we skip one draw from the wall
        if meld.opened:
            # but if it's an opened kan, player will get a tile from
            # a dead wall, so total number of tiles in the wall is the same
            # as if he just draws a tile
            if meld.type != MeldPrint.KAN and meld.type != meld.SHOUMINKAN:
                self.count_of_remaining_tiles += 1
        else:
            # can't have a pon or chi from the hand
            assert meld.type == MeldPrint.KAN or meld.type == meld.SHOUMINKAN
            # player draws additional tile from the wall in case of closed kan or shouminkan
            self.count_of_remaining_tiles -= 1

        self.get_player(player_seat).add_called_meld(meld)

        tiles = meld.tiles[:]
        # called tile was already added to revealed array
        # because it was called on the discard
        if meld.called_tile is not None:
            tiles.remove(meld.called_tile)

        # for shouminkan we already added 3 tiles
        if meld.type == meld.SHOUMINKAN:
            tiles = [meld.tiles[0]]

        for tile in tiles:
            self._add_revealed_tile(tile)

        for player in self.players:
            player.is_ippatsu = False

    def add_called_riichi_step_one(self, player_seat):
        """
        We need to mark player in riichi to properly defence against his riichi tile discard
        """
        player = self.get_player(player_seat)
        player.in_riichi = True

        # we had to check will we go for defence or not
        if player_seat != 0:
            self.player.enemy_called_riichi(player_seat)

    def add_called_riichi_step_two(self, player_seat):
        player = self.get_player(player_seat)

        if player.scores is not None:
            player.scores -= 1000

        self.count_of_riichi_sticks += 1

        player.is_ippatsu = True
        assert len(player.discards) >= 1, "Player had to have at least one discarded tile after riichi"
        latest_discard = player.discards[-1]
        latest_discard.riichi_discard = True
        player.riichi_tile_136 = latest_discard.value

        player.is_oikake_riichi = len([x for x in self.players if x.in_riichi]) > 1
        if not player.is_oikake_riichi:
            other_riichi_players = [x for x in self.players if x.in_riichi and x != player]
            player.is_oikake_riichi_against_dealer_riichi_threat = any([x.is_dealer for x in other_riichi_players])

        open_hand_threat = False
        for other_player in self.players:
            if other_player == player:
                continue

            for meld in other_player.melds:
                dora_number = 0
                if meld.type == MeldPrint.CHI:
                    continue

                for tile in meld.tiles:
                    dora_number += plus_dora(tile, self.dora_indicators, add_aka_dora=self.has_aka_dora)

                if dora_number >= 3:
                    open_hand_threat = True
        player.is_riichi_against_open_hand_threat = open_hand_threat

    def add_discarded_tile(self, player_seat, tile_136, is_tsumogiri):
        """
        :param player_seat:
        :param tile_136: 136 format tile
        :param is_tsumogiri: was tile discarded from hand or not
        """
        if player_seat != 0:
            self.count_of_remaining_tiles -= 1

        tile = Tile(tile_136, is_tsumogiri)
        tile.riichi_discard = False
        player = self.get_player(player_seat)
        player.add_discarded_tile(tile)

        self._add_revealed_tile(tile_136)

        player.is_ippatsu = False

    def add_dora_indicator(self, tile):
        self.dora_indicators.append(tile)
        self._add_revealed_tile(tile)

    def is_dora(self, tile):
        return plus_dora(tile, self.dora_indicators, add_aka_dora=self.has_aka_dora)

    def set_players_scores(self, scores, uma=None):
        for i in range(0, len(scores)):
            self.get_player(i).scores = scores[i] * 100

            if uma:
                self.get_player(i).uma = uma[i]

        self.recalculate_players_position()

    def recalculate_players_position(self):
        temp_players = self.get_players_sorted_by_scores()
        for i in range(0, len(temp_players)):
            temp_player = temp_players[i]
            self.get_player(temp_player.seat).position = i + 1

    def set_players_names_and_ranks(self, values):
        for x in range(0, len(values)):
            self.get_player(x).name = values[x]["name"]
            self.get_player(x).rank = values[x]["rank"]

    def get_player(self, player_seat):
        return self.players[player_seat]

    def get_players_sorted_by_scores(self):
        return sorted(self.players, key=lambda x: (x.scores or 0, -x.first_seat), reverse=True)

    @property
    def round_wind_tile(self):
        if self.round_wind_number < 4:
            return EAST
        elif 4 <= self.round_wind_number < 8:
            return SOUTH
        elif 8 <= self.round_wind_number < 12:
            return WEST
        else:
            return NORTH

    def is_common_yakuhai(self, tile_34):
        return is_sangenpai(tile_34) or tile_34 == self.round_wind_tile

    def _add_revealed_tile(self, tile):
        self.revealed_tiles_136.append(tile)
        tile_34 = tile // 4
        self.revealed_tiles[tile_34] += 1

        assert (
            self.revealed_tiles[tile_34] <= 4
        ), f"we have only 4 tiles in the game: {TilesConverter.to_one_line_string([tile])}"

    def _init_players(self, bot_config):
        self.player = Player(self, 0, self.dealer_seat, bot_config)

        self.players = [self.player]
        for seat in range(1, self.count_of_players):
            player = EnemyPlayer(self, seat, self.dealer_seat)
            self.players.append(player)
