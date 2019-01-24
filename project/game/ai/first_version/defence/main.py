from mahjong.tile import TilesConverter
from mahjong.utils import is_honor

from game.ai.first_version.helpers.defence import TileDanger
from game.ai.first_version.defence.enemy_analyzer import EnemyAnalyzer


class DefenceHandler:
    player = None
    _analyzed_enemies = None

    def __init__(self, player):
        self.player = player
        self._analyzed_enemies = None

    def calculate_tiles_danger(self, discard_candidates):
        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)

        common_tiles_danger = {}
        for x in range(0, 34):
            common_tiles_danger[x] = []

        # something that could be applied to all enemies together
        for discard_option in discard_candidates:
            tile_34 = discard_option.tile_to_discard

            if is_honor(tile_34):
                total_tiles = self.player.total_tiles(tile_34, closed_hand_34)

                if total_tiles == 3:
                    common_tiles_danger[tile_34].append(TileDanger.HONOR_THIRD)

        for enemy in self.analyzed_enemies:
            # tiles danger common to all enemy players
            for tile_34 in common_tiles_danger.keys():
                for tile_danger in common_tiles_danger[tile_34]:
                    self._update_discard_candidate(
                        tile_34,
                        discard_candidates,
                        enemy.player.seat,
                        tile_danger
                    )

            # genbutsu tiles
            for safe_tile_34 in enemy.player.all_safe_tiles:
                if closed_hand_34[safe_tile_34] == 0:
                    continue

                self._update_discard_candidate(
                    safe_tile_34,
                    discard_candidates,
                    enemy.player.seat,
                    TileDanger.GENBUTSU
                )

            # safe tiles that can be safe based on the table situation
            for tile_34 in range(0, 34):
                if closed_hand_34[tile_34] == 0:
                    continue

                if enemy.total_possible_forms_for_tile(tile_34) == 0:
                    self._update_discard_candidate(
                        tile_34,
                        discard_candidates,
                        enemy.player.seat,
                        TileDanger.IMPOSSIBLE_WAIT
                    )

        return discard_candidates

    @property
    def analyzed_enemies(self):
        if self._analyzed_enemies:
            return self._analyzed_enemies

        self._analyzed_enemies = [EnemyAnalyzer(enemy) for enemy in self.player.ai.enemy_players]
        return self._analyzed_enemies

    def _get_threatening_players(self):
        result = []
        for player in self.analyzed_enemies:
            if player.is_threatening:
                result.append(player)
        return result

    def _update_discard_candidate(self, tile_34, discard_candidates, player, danger):
        for discard_candidate in discard_candidates:
            if discard_candidate.tile_to_discard == tile_34:
                discard_candidate.danger.set_danger(player, danger)
