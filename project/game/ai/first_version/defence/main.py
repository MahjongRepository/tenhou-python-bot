from mahjong.tile import TilesConverter
from mahjong.utils import is_honor

from game.ai.first_version.helpers.defence import TileDanger
from game.ai.first_version.defence.enemy_analyzer import EnemyAnalyzer


class DefenceHandler:
    table = None
    player = None

    def __init__(self, player):
        self.table = player.table
        self.player = player

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

            for enemy in threatening_players:
                if enemy.total_possible_forms_for_tile(tile_34) == 0:
                    self._update_discard_candidate(
                        tile_34,
                        discard_candidates,
                        enemy.player.seat,
                        TileDanger.IMPOSSIBLE_WAIT
                    )

        # let's calculate danger level for every user
        for enemy in threatening_players:
            for safe_tile_34 in enemy.player.all_safe_tiles:
                self._update_discard_candidate(
                    safe_tile_34,
                    discard_candidates,
                    enemy.player.seat,
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
        result = []
        for player in self.analyzed_enemies:
            if player.is_threatening:
                result.append(player)
        return result

    def _mark_safe_tiles_against_honitsu(self, player):
        against_honitsu = []
        for tile in range(0, 34):
            if not self.closed_hand_34[tile]:
                continue

            if not player.chosen_suit(tile) and not is_honor(tile):
                against_honitsu.append(tile)

        return against_honitsu

    def _update_discard_candidate(self, tile_34, discard_candidates, player, danger):
        for discard_candidate in discard_candidates:
            if discard_candidate.tile_to_discard == tile_34:
                discard_candidate.danger.set_danger(player, danger)
