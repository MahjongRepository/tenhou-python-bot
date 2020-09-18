from typing import List

from game.ai.defence.enemy_analyzer import EnemyAnalyzer
from game.ai.discard import DiscardOption
from game.ai.helpers.defence import TileDanger
from game.ai.helpers.possible_forms import PossibleFormsAnalyzer
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor


class DefenceHandler:
    player = None
    _analyzed_enemies: List[EnemyAnalyzer] = None

    def __init__(self, player):
        self.player = player
        self._analyzed_enemies = []
        self.possible_forms_analyzer = PossibleFormsAnalyzer(self.player)

    def calculate_tiles_danger(
        self, discard_candidates: List[DiscardOption], enemy: EnemyAnalyzer
    ) -> List[DiscardOption]:
        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)

        possible_forms = self.possible_forms_analyzer.calculate_possible_forms(enemy.all_safe_tiles)
        for discard_option in discard_candidates:
            tile_34 = discard_option.tile_to_discard

            # special rules for honor
            if is_honor(tile_34):
                total_tiles = self.player.total_tiles(tile_34, closed_hand_34)

                if total_tiles == 1:
                    if tile_34 not in enemy.player.valued_honors:
                        self._update_discard_candidate(
                            tile_34,
                            discard_candidates,
                            enemy.player.seat,
                            TileDanger.NON_YAKUHAI_HONOR_SHONPAI,
                        )

                if total_tiles == 2:
                    if tile_34 not in enemy.player.valued_honors:
                        self._update_discard_candidate(
                            tile_34,
                            discard_candidates,
                            enemy.player.seat,
                            TileDanger.NON_YAKUHAI_HONOR_SECOND,
                        )

                if total_tiles == 3:
                    self._update_discard_candidate(
                        tile_34,
                        discard_candidates,
                        enemy.player.seat,
                        TileDanger.HONOR_THIRD,
                    )

            # genbutsu
            if tile_34 in enemy.player.all_safe_tiles:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy.player.seat,
                    TileDanger.GENBUTSU,
                )

            # safe tiles that can be safe based on the table situation
            if self.total_possible_forms_for_tile(possible_forms, tile_34) == 0:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy.player.seat,
                    TileDanger.IMPOSSIBLE_WAIT,
                )

            forms_count = possible_forms[tile_34]
            self._update_discard_candidate(
                tile_34,
                discard_candidates,
                enemy.player.seat,
                {
                    "value": self.possible_forms_analyzer.calculate_possible_forms_danger(forms_count),
                    "description": TileDanger.FORM_BONUS_DESCRIPTION,
                    "forms_count": forms_count,
                },
            )

        return discard_candidates

    def check_threat_and_mark_tiles_danger(self, discard_candidates):
        threatening_players = self._get_threatening_players()
        for threatening_player in threatening_players:
            discard_candidates = self.calculate_tiles_danger(discard_candidates, threatening_player)
        return discard_candidates

    def total_possible_forms_for_tile(self, possible_forms, tile_34):
        forms_count = possible_forms[tile_34]
        assert forms_count is not None
        return self.possible_forms_analyzer.calculate_possible_forms_total(forms_count)

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
