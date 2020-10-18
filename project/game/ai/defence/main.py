from copy import copy
from typing import List

from game.ai.defence.enemy_analyzer import EnemyAnalyzer
from game.ai.discard import DiscardOption
from game.ai.helpers.defence import TileDanger
from game.ai.helpers.kabe import Kabe
from game.ai.helpers.possible_forms import PossibleFormsAnalyzer
from mahjong.tile import TilesConverter
from mahjong.utils import is_aka_dora, is_honor, is_terminal, plus_dora


class TileDangerHandler:
    player = None
    _analyzed_enemies: List[EnemyAnalyzer] = None

    def __init__(self, player):
        self.player = player
        self._analyzed_enemies = []

        self.possible_forms_analyzer = PossibleFormsAnalyzer(player)

    def calculate_tiles_danger(
        self, discard_candidates: List[DiscardOption], enemy_analyzer: EnemyAnalyzer
    ) -> List[DiscardOption]:
        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)

        safe_against_threat_34 = []
        if enemy_analyzer.threat_reason.get("active_yaku"):
            for x in enemy_analyzer.threat_reason.get("active_yaku"):
                safe_against_threat_34.extend(x.get_safe_tiles_34())

        possible_forms = self.possible_forms_analyzer.calculate_possible_forms(enemy_analyzer.enemy.all_safe_tiles)
        kabe_tiles = self.player.ai.kabe.find_all_kabe(closed_hand_34)
        suji_tiles = self.player.ai.suji.find_suji([x.value for x in enemy_analyzer.enemy.discards])
        for discard_option in discard_candidates:
            tile_34 = discard_option.tile_to_discard
            tile_136 = discard_option.find_tile_in_hand(self.player.closed_hand)
            number_of_revealed_tiles = self.player.number_of_revealed_tiles(tile_34, closed_hand_34)

            # like 1-9 against tanya etc.
            if tile_34 in safe_against_threat_34:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy_analyzer.enemy.seat,
                    TileDanger.SAFE_AGAINST_THREATENING_HAND,
                )
                continue

            # safe tiles that can be safe based on the table situation
            if self.total_possible_forms_for_tile(possible_forms, tile_34) == 0:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy_analyzer.enemy.seat,
                    TileDanger.IMPOSSIBLE_WAIT,
                )
                continue

            # honors
            if is_honor(tile_34):
                danger = self._process_danger_for_honor(tile_34, enemy_analyzer, number_of_revealed_tiles)
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
                    enemy_analyzer.enemy.seat,
                    danger,
                )

            forms_count = possible_forms[tile_34]
            self._update_discard_candidate(
                tile_34,
                discard_candidates,
                enemy_analyzer.enemy.seat,
                {
                    "value": self.possible_forms_analyzer.calculate_possible_forms_danger(forms_count),
                    "description": TileDanger.FORM_BONUS_DESCRIPTION,
                    "forms_count": forms_count,
                },
            )

            if forms_count[PossibleFormsAnalyzer.POSSIBLE_RYANMEN] > 0:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy_analyzer.enemy.seat,
                    TileDanger.RYANMEN_BASE,
                )

            dora_count = plus_dora(tile_136, self.player.table.dora_indicators)
            if is_aka_dora(tile_136, self.player.table.has_aka_dora):
                dora_count += 1

            if dora_count > 0:
                danger = copy(TileDanger.DORA_BONUS)
                danger["value"] = dora_count * danger["value"]
                danger["dora_count"] = dora_count
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy_analyzer.enemy.seat,
                    danger,
                )

        return discard_candidates

    def calculate_danger_borders(self, discard_options, threatening_player):
        for discard_option in discard_options:
            danger_border = TileDanger.DEFAULT_DANGER_BORDER

            # TODO add other shanten cases
            if discard_option.shanten == 0:
                threatening_player_hand_cost = threatening_player.threat_reason["assumed_hand_cost"]
                threatening_danger_border = threatening_player.threat_reason["danger_border"]
                hand_weighted_cost = self.player.ai.estimate_weighted_mean_hand_value(discard_option)
                discard_option.danger.weighted_cost = hand_weighted_cost
                cost_ratio = (hand_weighted_cost / threatening_player_hand_cost) * 100

                # good wait
                if discard_option.ukeire >= 6:
                    if cost_ratio > 100:
                        danger_border = TileDanger.IGNORE_DANGER
                    elif cost_ratio > 70:
                        danger_border = 200 - threatening_danger_border
                    elif cost_ratio > 40:
                        danger_border = 120 - threatening_danger_border
                    else:
                        danger_border = 60
                # moderate wait
                elif discard_option.ukeire >= 4:
                    if cost_ratio >= 200:
                        danger_border = 300 - threatening_danger_border
                    elif cost_ratio >= 100:
                        danger_border = 220 - threatening_danger_border
                    elif cost_ratio >= 70:
                        danger_border = 180 - threatening_danger_border
                    elif cost_ratio >= 40:
                        danger_border = 100 - threatening_danger_border
                    else:
                        danger_border = 50
                # weak wait
                else:
                    if cost_ratio >= 200:
                        danger_border = 250 - threatening_danger_border
                    elif cost_ratio >= 100:
                        danger_border = 200 - threatening_danger_border
                    elif cost_ratio >= 70:
                        danger_border = 150 - threatening_danger_border
                    elif cost_ratio >= 40:
                        danger_border = 60 - threatening_danger_border
                    else:
                        danger_border = 40

            discard_option.danger.danger_border = danger_border
        return discard_options

    def mark_tiles_danger_for_threats(self, discard_options):
        threatening_players = self._get_threatening_players()
        for threatening_player in threatening_players:
            discard_options = self.calculate_tiles_danger(discard_options, threatening_player)
            discard_options = self.calculate_danger_borders(discard_options, threatening_player)
        return discard_options, len(threatening_players) > 0

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
        number_of_yakuhai = enemy.enemy.valued_honors.count(tile_34)

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

    def _update_discard_candidate(self, tile_34, discard_candidates, player_seat, danger):
        for discard_candidate in discard_candidates:
            if discard_candidate.tile_to_discard == tile_34:
                # we found safe tile, in that case we can ignore all other metrics
                if danger["value"] == 0:
                    discard_candidate.danger.clear_danger(player_seat)

                # let's put danger metrics to the tile only if there is no safe tiles in the hand
                has_safe = (
                    len([x for x in discard_candidate.danger.get_danger_reasons(player_seat) if x["value"] == 0]) == 1
                )
                if not has_safe:
                    discard_candidate.danger.set_danger(player_seat, danger)
