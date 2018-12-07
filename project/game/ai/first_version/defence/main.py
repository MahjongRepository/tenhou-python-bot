from mahjong.constants import EAST
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor
from mahjong.utils import simplify, is_man, is_pin, is_sou

from game.ai.first_version.defence.defence import TileDanger
from game.ai.first_version.defence.enemy_analyzer import EnemyAnalyzer
from game.ai.first_version.defence.kabe import Kabe
from game.ai.first_version.defence.suji import Suji


class DefenceHandler:
    table = None
    player = None

    # different strategies
    kabe = None
    suji = None

    # cached values, that will be used by all strategies
    hand_34 = None
    closed_hand_34 = None

    def __init__(self, player):
        self.table = player.table
        self.player = player

        self.kabe = Kabe(self)
        self.suji = Suji(self)

        self.hand_34 = None
        self.closed_hand_34 = None

    def calculate_tiles_danger(self, discard_candidates):
        threatening_players = self._get_threatening_players()

        # there is no threat
        # so we don't want to spend time on safe tiles calculation
        if not threatening_players:
            return discard_candidates

        self.hand_34 = TilesConverter.to_34_array(self.player.tiles)
        self.closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)

        # safe tiles that can be safe based on the table situation
        for tile_34 in range(0, 34):
            if self.closed_hand_34[tile_34] == 0:
                continue

            is_safe = True
            for enemy in threatening_players:
                is_safe = is_safe and enemy.total_possible_forms_for_tile(tile_34) == 0

            if is_safe:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    'all',
                    TileDanger.IMPOSSIBLE_WAIT
                )

        # let's calculate danger level for every user
        for analyzed_player in threatening_players:
            for safe_tile_34 in analyzed_player.player.all_safe_tiles:
                self._update_discard_candidate(
                    safe_tile_34,
                    discard_candidates,
                    analyzed_player.player.seat,
                    TileDanger.GENBUTSU
                )
            # player_suji_tiles = self.suji.find_tiles_to_discard([player])
            #
            # # better to not use suji for honitsu hands
            # if not player.chosen_suit:
            #     player_safe_tiles += player_suji_tiles
            #
            # # try to find safe tiles against honitsu
            # if player.chosen_suit:
            #     against_honitsu = self._mark_safe_tiles_against_honitsu(player)
            #     against_honitsu = [DefenceTile(x, DefenceTile.SAFE) for x in against_honitsu]
            #
            #     result = self._find_tile_to_discard(against_honitsu, discard_results)
            #     if result:
            #         return result

        return discard_candidates

    @property
    def analyzed_enemies(self):
        players = self.player.ai.enemy_players
        return [EnemyAnalyzer(self, x) for x in players]

    def _get_threatening_players(self):
        """
        For now it is just players in riichi,
        later I will add players with opened valuable hands.
        Sorted by threat level. Most threatening on the top
        """
        result = []
        for player in self.analyzed_enemies:
            if player.is_threatening:
                result.append(player)

        # dealer is most threatening player
        result = sorted(result, key=lambda x: x.player.is_dealer, reverse=True)

        return result

    def _mark_safe_tiles_against_honitsu(self, player):
        against_honitsu = []
        for tile in range(0, 34):
            if not self.closed_hand_34[tile]:
                continue

            if not player.chosen_suit(tile) and not is_honor(tile):
                against_honitsu.append(tile)

        return against_honitsu

    def _suits_tiles(self, tiles_34):
        """
        Return tiles separated by suits
        :param tiles_34:
        :return:
        """
        suits = [
            [0] * 9,
            [0] * 9,
            [0] * 9,
        ]

        for tile in range(0, EAST):
            total_tiles = self.player.total_tiles(tile, tiles_34)
            if not total_tiles:
                continue

            suit_index = None
            simplified_tile = simplify(tile)

            if is_man(tile):
                suit_index = 0

            if is_pin(tile):
                suit_index = 1

            if is_sou(tile):
                suit_index = 2

            suits[suit_index][simplified_tile] += total_tiles

        return suits

    def _update_discard_candidate(self, tile_34, discard_candidates, player, danger):
        for discard_candidate in discard_candidates:
            if discard_candidate.tile_to_discard == tile_34:
                discard_candidate.danger.set_danger(player, danger)
