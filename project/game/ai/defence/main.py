from typing import List

from game.ai.defence.enemy_analyzer import EnemyAnalyzer
from game.ai.discard import DiscardOption
from game.ai.helpers.defence import TileDanger
from game.ai.helpers.kabe import Kabe
from game.ai.helpers.possible_forms import PossibleFormsAnalyzer
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor, is_terminal


class DefenceHandler:
    player = None
    _analyzed_enemies: List[EnemyAnalyzer] = None

    def __init__(self, player):
        self.player = player
        self._analyzed_enemies = []

        self.possible_forms_analyzer = PossibleFormsAnalyzer(player)

    def calculate_tiles_danger(
        self, discard_candidates: List[DiscardOption], enemy: EnemyAnalyzer
    ) -> List[DiscardOption]:
        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)

        possible_forms = self.possible_forms_analyzer.calculate_possible_forms(enemy.all_safe_tiles)
        kabe_tiles = self.player.ai.kabe.find_all_kabe(closed_hand_34)
        suji_tiles = self.player.ai.suji.find_suji([x.value for x in enemy.player.discards])
        for discard_option in discard_candidates:
            tile_34 = discard_option.tile_to_discard
            number_of_revealed_tiles = self.player.number_of_revealed_tiles(tile_34, closed_hand_34)

            # safe tiles that can be safe based on the table situation
            if self.total_possible_forms_for_tile(possible_forms, tile_34) == 0:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy.player.seat,
                    TileDanger.IMPOSSIBLE_WAIT,
                )
                continue

            danger = None
            # honors
            if is_honor(tile_34):
                danger = self._process_danger_for_honor(tile_34, enemy, number_of_revealed_tiles)
            # terminals
            elif is_terminal(tile_34):
                danger = self._process_danger_for_terminal_tiles_and_kabe_suji(
                    tile_34, number_of_revealed_tiles, kabe_tiles, suji_tiles
                )
            # 2-8 tiles
            else:
                danger = self._process_danger_for_2_8_tiles_and_kabe(tile_34, number_of_revealed_tiles, kabe_tiles)

            if danger:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy.player.seat,
                    danger,
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

    def _process_danger_for_terminal_tiles_and_kabe_suji(
        self, tile_34, number_of_revealed_tiles, kabe_tiles, suji_tiles
    ):
        have_strong_kabe = [x for x in kabe_tiles if tile_34 == x["tile"] and x["type"] == Kabe.STRONG_KABE]
        if have_strong_kabe:
            if number_of_revealed_tiles == 1:
                return TileDanger.SHONPAI_KABE
            else:
                return TileDanger.NON_SHONPAI_KABE

        if tile_34 in suji_tiles:
            if number_of_revealed_tiles == 1:
                return TileDanger.SUJI_19_SHONPAI
            else:
                return TileDanger.SUJI_19_NOT_SHONPAI

        return None

    def _process_danger_for_2_8_tiles_and_kabe(self, tile_34, number_of_revealed_tiles, kabe_tiles):
        have_strong_kabe = [x for x in kabe_tiles if tile_34 == x["tile"] and x["type"] == Kabe.STRONG_KABE]
        if have_strong_kabe:
            if number_of_revealed_tiles == 1:
                return TileDanger.SHONPAI_KABE
            else:
                return TileDanger.NON_SHONPAI_KABE
        return None

    def _process_danger_for_honor(self, tile_34, enemy, number_of_revealed_tiles):
        danger = None
        number_of_yakuhai = enemy.player.valued_honors.count(tile_34)

        if number_of_revealed_tiles == 1:
            if number_of_yakuhai == 0:
                danger = TileDanger.NON_YAKUHAI_HONOR_SHONPAI
            if number_of_yakuhai == 1:
                danger = TileDanger.YAKUHAI_HONOR_SHONPAI
            if number_of_yakuhai == 2:
                danger = TileDanger.DOUBLE_YAKUHAI_HONOR_SHONPAI

        if number_of_revealed_tiles == 2:
            if number_of_yakuhai == 0:
                danger = TileDanger.NON_YAKUHAI_HONOR_SECOND
            if number_of_yakuhai == 1:
                danger = TileDanger.YAKUHAI_HONOR_SECOND
            if number_of_yakuhai == 2:
                danger = TileDanger.DOUBLE_YAKUHAI_HONOR_SECOND

        if number_of_revealed_tiles == 3:
            danger = TileDanger.HONOR_THIRD

        return danger

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
