from copy import copy
from typing import List

from game.ai.defence.enemy_analyzer import EnemyAnalyzer
from game.ai.discard import DiscardOption
from game.ai.helpers.defence import DangerBorder, TileDanger
from game.ai.helpers.kabe import Kabe
from game.ai.helpers.possible_forms import PossibleFormsAnalyzer
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor, is_man, is_pin, is_sou, is_terminal, plus_dora, simplify
from utils.general import is_tiles_same_suit


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

        # First, add all genbutsu to the list
        safe_against_threat_34.extend(list(set([x for x in enemy_analyzer.enemy.all_safe_tiles])))

        # Then add tiles not suitable for yaku in enemy open hand
        if enemy_analyzer.threat_reason.get("active_yaku"):
            safe_against_yaku = set.intersection(
                *[set(x.get_safe_tiles_34()) for x in enemy_analyzer.threat_reason.get("active_yaku")]
            )
            if safe_against_yaku:
                safe_against_threat_34.extend(list(safe_against_yaku))

        possible_forms = self.possible_forms_analyzer.calculate_possible_forms(enemy_analyzer.enemy.all_safe_tiles)
        kabe_tiles = self.player.ai.kabe.find_all_kabe(closed_hand_34)
        suji_tiles = self.player.ai.suji.find_suji([x.value for x in enemy_analyzer.enemy.discards])
        for discard_option in discard_candidates:
            tile_34 = discard_option.tile_to_discard_34
            tile_136 = discard_option.find_tile_in_hand(self.player.closed_hand)
            number_of_revealed_tiles = self.player.number_of_revealed_tiles(tile_34, closed_hand_34)

            # like 1-9 against tanyao etc.
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
                danger = self._process_danger_for_honor(enemy_analyzer, tile_34, number_of_revealed_tiles)
            # terminals
            elif is_terminal(tile_34):
                danger = self._process_danger_for_terminal_tiles_and_kabe_suji(
                    enemy_analyzer, tile_34, number_of_revealed_tiles, kabe_tiles, suji_tiles
                )
            # 2-8 tiles
            else:
                danger = self._process_danger_for_2_8_tiles_suji_and_kabe(
                    enemy_analyzer, tile_34, number_of_revealed_tiles, suji_tiles, kabe_tiles
                )

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

            # for ryanmen waits we also account for number of dangerous suji tiles
            forms_ryanmen_count = forms_count[PossibleFormsAnalyzer.POSSIBLE_RYANMEN_SIDES]
            if forms_ryanmen_count == 1:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy_analyzer.enemy.seat,
                    TileDanger.RYANMEN_BASE_SINGLE,
                )
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy_analyzer.enemy.seat,
                    TileDanger.make_unverified_suji_coeff(enemy_analyzer.unverified_suji_coeff),
                )
            elif forms_ryanmen_count == 2:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy_analyzer.enemy.seat,
                    TileDanger.RYANMEN_BASE_DOUBLE,
                )
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy_analyzer.enemy.seat,
                    TileDanger.make_unverified_suji_coeff(enemy_analyzer.unverified_suji_coeff),
                )

            if forms_ryanmen_count == 1 or forms_ryanmen_count == 2:
                # check if there any matagi-suji pattern for tiles that could be used in ryanmen
                if self._is_matagi_suji(enemy_analyzer, tile_34):
                    self._update_discard_candidate(
                        tile_34,
                        discard_candidates,
                        enemy_analyzer.enemy.seat,
                        TileDanger.BONUS_MATAGI_SUJI,
                    )
                # check if there any aidayonken pattern for tiles that could be used in ryanmen
                if self.is_aidayonken_pattern(enemy_analyzer, tile_34):
                    self._update_discard_candidate(
                        tile_34,
                        discard_candidates,
                        enemy_analyzer.enemy.seat,
                        TileDanger.BONUS_AIDAYONKEN,
                    )

            dora_count = plus_dora(
                tile_136, self.player.table.dora_indicators, add_aka_dora=self.player.table.has_aka_dora
            )

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

            if enemy_analyzer.threat_reason.get("active_yaku"):
                for yaku_analyzer in enemy_analyzer.threat_reason.get("active_yaku"):
                    bonus_danger = yaku_analyzer.get_bonus_danger(tile_136, number_of_revealed_tiles)
                    for danger in bonus_danger:
                        self._update_discard_candidate(
                            tile_34,
                            discard_candidates,
                            enemy_analyzer.enemy.seat,
                            danger,
                        )

        return discard_candidates

    def calculate_danger_borders(self, discard_options, threatening_player):
        min_shanten = min([x.shanten for x in discard_options])

        placement_adjustment = self.player.ai.placement.get_allowed_danger_modifier()
        for discard_option in discard_options:
            danger_border = DangerBorder.BETAORI
            hand_weighted_cost = 0
            tune = 0
            shanten = discard_option.shanten
            tile_136 = discard_option.tile_to_discard_136

            if discard_option.danger.get_total_danger_for_player(threatening_player.enemy.seat) == 0:
                threatening_player_hand_cost = 0
            else:
                threatening_player_hand_cost = threatening_player.get_assumed_hand_cost(tile_136)

            # fast path: we don't need to calculate all the stuff if this tile is safe against this enemy
            if threatening_player_hand_cost == 0:
                discard_option.danger.set_danger_border(
                    threatening_player.enemy.seat, DangerBorder.IGNORE, hand_weighted_cost, threatening_player_hand_cost
                )
                continue

            # never push with zero chance to win
            # FIXME: we may actually want to push it for tempai in ryukoku, so reconsider
            if discard_option.ukeire == 0:
                discard_option.danger.set_danger_border(
                    threatening_player.enemy.seat,
                    DangerBorder.BETAORI,
                    hand_weighted_cost,
                    threatening_player_hand_cost,
                )
                continue

            if discard_option.shanten == 0:
                hand_weighted_cost = self.player.ai.estimate_weighted_mean_hand_value(discard_option)
                discard_option.danger.weighted_cost = hand_weighted_cost
                cost_ratio = (hand_weighted_cost / threatening_player_hand_cost) * 100
                tune = self.player.config.TUNE_DANGER_BORDER_TEMPAI_VALUE

                # good wait
                if discard_option.ukeire >= 6:
                    if cost_ratio >= 100:
                        danger_border = DangerBorder.IGNORE
                    elif cost_ratio >= 70:
                        danger_border = DangerBorder.VERY_HIGH
                    elif cost_ratio >= 50:
                        danger_border = DangerBorder.UPPER_MEDIUM
                    elif cost_ratio >= 30:
                        danger_border = DangerBorder.MEDIUM
                    else:
                        danger_border = DangerBorder.LOW
                # moderate wait
                elif discard_option.ukeire >= 4:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.IGNORE
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.EXTREME
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.VERY_HIGH
                    elif cost_ratio >= 70:
                        danger_border = DangerBorder.UPPER_MEDIUM
                    elif cost_ratio >= 50:
                        danger_border = DangerBorder.LOWER_MEDIUM
                    elif cost_ratio >= 30:
                        danger_border = DangerBorder.UPPER_LOW
                    else:
                        danger_border = DangerBorder.VERY_LOW
                # weak wait
                elif discard_option.ukeire >= 2:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.EXTREME
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.VERY_HIGH
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.UPPER_MEDIUM
                    elif cost_ratio >= 70:
                        danger_border = DangerBorder.MEDIUM
                    elif cost_ratio >= 50:
                        danger_border = DangerBorder.UPPER_LOW
                    elif cost_ratio >= 30:
                        danger_border = DangerBorder.LOW
                    else:
                        danger_border = DangerBorder.EXTREMELY_LOW
                # waiting for 1 tile basically
                else:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.HIGH
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.UPPER_MEDIUM
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.LOWER_MEDIUM
                    elif cost_ratio >= 50:
                        danger_border = DangerBorder.LOW
                    else:
                        danger_border = DangerBorder.EXTREMELY_LOW

            if discard_option.shanten == 1:
                tune = self.player.config.TUNE_DANGER_BORDER_1_SHANTEN_VALUE

                # FIXME: temporary solution to avoid too much ukeire2 calculation
                if min_shanten == 0:
                    hand_weighted_cost = 2000
                else:
                    hand_weighted_cost = discard_option.average_second_level_cost

                # never push with zero chance to win
                # FIXME: we may actually want to push it for tempai in ryukoku, so reconsider
                if not hand_weighted_cost:
                    discard_option.danger.set_danger_border(
                        threatening_player.enemy.seat,
                        DangerBorder.BETAORI,
                        hand_weighted_cost,
                        threatening_player_hand_cost,
                    )
                    continue

                discard_option.danger.weighted_cost = int(hand_weighted_cost)
                cost_ratio = (hand_weighted_cost / threatening_player_hand_cost) * 100

                # lots of ukeire
                if discard_option.ukeire >= 32:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.IGNORE
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.EXTREME
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.VERY_HIGH
                    elif cost_ratio >= 50:
                        danger_border = DangerBorder.MEDIUM
                    elif cost_ratio >= 20:
                        danger_border = DangerBorder.UPPER_LOW
                    else:
                        danger_border = DangerBorder.EXTREMELY_LOW
                # very good ukeire
                elif discard_option.ukeire >= 20:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.IGNORE
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.EXTREME
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.VERY_HIGH
                    elif cost_ratio >= 50:
                        danger_border = DangerBorder.LOWER_MEDIUM
                    elif cost_ratio >= 20:
                        danger_border = DangerBorder.LOW
                    else:
                        danger_border = DangerBorder.EXTREMELY_LOW
                # good ukeire
                elif discard_option.ukeire >= 12:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.VERY_HIGH
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.HIGH
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.UPPER_MEDIUM
                    elif cost_ratio >= 50:
                        danger_border = DangerBorder.UPPER_LOW
                    elif cost_ratio >= 20:
                        danger_border = DangerBorder.VERY_LOW
                    else:
                        danger_border = DangerBorder.BETAORI
                # mediocre ukeire
                elif discard_option.ukeire >= 7:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.HIGH
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.UPPER_MEDIUM
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.LOWER_MEDIUM
                    elif cost_ratio >= 50:
                        danger_border = DangerBorder.VERY_LOW
                    elif cost_ratio >= 20:
                        danger_border = DangerBorder.LOWEST
                    else:
                        danger_border = DangerBorder.BETAORI
                # very low ukeire
                elif discard_option.ukeire >= 3:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.MEDIUM
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.UPPER_LOW
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.VERY_LOW
                    elif cost_ratio >= 50:
                        danger_border = DangerBorder.LOWEST
                    else:
                        danger_border = DangerBorder.BETAORI
                # little to no ukeire
                else:
                    danger_border = DangerBorder.BETAORI

            if discard_option.shanten == 2:
                tune = self.player.config.TUNE_DANGER_BORDER_2_SHANTEN_VALUE

                if self.player.is_dealer:
                    scale = [0, 1000, 2900, 5800, 7700, 12000, 18000, 18000, 24000, 24000, 48000]
                else:
                    scale = [0, 1000, 2000, 3900, 5200, 8000, 12000, 12000, 16000, 16000, 32000]

                if self.player.is_open_hand:
                    # FIXME: each strategy should have a han value, we should use it instead
                    han = 1
                else:
                    # TODO: try to estimate yaku chances for closed hand
                    han = 1

                dora_count = sum(
                    [
                        plus_dora(x, self.player.table.dora_indicators, add_aka_dora=self.player.table.has_aka_dora)
                        for x in self.player.tiles
                    ]
                )

                han += dora_count

                hand_weighted_cost = scale[min(han, len(scale) - 1)]

                discard_option.danger.weighted_cost = int(hand_weighted_cost)
                cost_ratio = (hand_weighted_cost / threatening_player_hand_cost) * 100

                # lots of ukeire
                if discard_option.ukeire >= 40:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.HIGH
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.MEDIUM
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.EXTREMELY_LOW
                    else:
                        danger_border = DangerBorder.BETAORI
                # very good ukeire
                elif discard_option.ukeire >= 20:
                    if cost_ratio >= 400:
                        danger_border = DangerBorder.UPPER_MEDIUM
                    elif cost_ratio >= 200:
                        danger_border = DangerBorder.LOW
                    elif cost_ratio >= 100:
                        danger_border = DangerBorder.LOWEST
                    else:
                        danger_border = DangerBorder.BETAORI
                # mediocre ukeire or worse
                else:
                    danger_border = DangerBorder.BETAORI

            # if we could have chosen tempai, pushing 1 or more shanten is usually
            # a pretty bad idea, so tune down
            if discard_option.shanten != 0 and min_shanten == 0:
                danger_border = DangerBorder.tune_down(danger_border, 2)

            # depending on our placement we may want to be more defensive or more offensive
            tune += placement_adjustment
            danger_border = DangerBorder.tune(danger_border, tune)

            # if it's late there are generally less reasons to be aggressive
            danger_border = DangerBorder.tune_for_round(self.player, danger_border, shanten)

            discard_option.danger.set_danger_border(
                threatening_player.enemy.seat, danger_border, hand_weighted_cost, threatening_player_hand_cost
            )
        return discard_options

    def get_threatening_players(self):
        result = []
        for player in self.analyzed_enemies:
            if player.is_threatening:
                result.append(player)
        return result

    def mark_tiles_danger_for_threats(self, discard_options):
        threatening_players = self.get_threatening_players()
        for threatening_player in threatening_players:
            discard_options = self.calculate_tiles_danger(discard_options, threatening_player)
            discard_options = self.calculate_danger_borders(discard_options, threatening_player)
        return discard_options, threatening_players

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
        self, enemy_analyzer, tile_34, number_of_revealed_tiles, kabe_tiles, suji_tiles
    ):
        have_strong_kabe = [x for x in kabe_tiles if tile_34 == x["tile"] and x["type"] == Kabe.STRONG_KABE]
        if have_strong_kabe:
            if enemy_analyzer.enemy.is_open_hand:
                if number_of_revealed_tiles == 1:
                    return TileDanger.SHONPAI_KABE_STRONG_OPEN_HAND
                else:
                    return TileDanger.NON_SHONPAI_KABE_STRONG_OPEN_HAND
            else:
                if number_of_revealed_tiles == 1:
                    return TileDanger.SHONPAI_KABE_STRONG
                else:
                    return TileDanger.NON_SHONPAI_KABE_STRONG

        if tile_34 in suji_tiles:
            if enemy_analyzer.enemy.is_open_hand:
                if number_of_revealed_tiles == 1:
                    return TileDanger.SUJI_19_SHONPAI_OPEN_HAND
                else:
                    return TileDanger.SUJI_19_NOT_SHONPAI_OPEN_HAND
            else:
                if number_of_revealed_tiles == 1:
                    return TileDanger.SUJI_19_SHONPAI
                else:
                    return TileDanger.SUJI_19_NOT_SHONPAI

        return None

    def _process_danger_for_2_8_tiles_suji_and_kabe(
        self, enemy_analyzer, tile_34, number_of_revealed_tiles, suji_tiles, kabe_tiles
    ):
        have_strong_kabe = [x for x in kabe_tiles if tile_34 == x["tile"] and x["type"] == Kabe.STRONG_KABE]
        if have_strong_kabe:
            if enemy_analyzer.enemy.is_open_hand:
                if number_of_revealed_tiles == 1:
                    return TileDanger.SHONPAI_KABE_STRONG_OPEN_HAND
                else:
                    return TileDanger.NON_SHONPAI_KABE_STRONG_OPEN_HAND
            else:
                if number_of_revealed_tiles == 1:
                    return TileDanger.SHONPAI_KABE_STRONG
                else:
                    return TileDanger.NON_SHONPAI_KABE_STRONG

        have_weak_kabe = [x for x in kabe_tiles if tile_34 == x["tile"] and x["type"] == Kabe.WEAK_KABE]
        if have_weak_kabe:
            if enemy_analyzer.enemy.is_open_hand:
                if number_of_revealed_tiles == 1:
                    return TileDanger.SHONPAI_KABE_WEAK_OPEN_HAND
                else:
                    return TileDanger.NON_SHONPAI_KABE_WEAK_OPEN_HAND
            else:
                if number_of_revealed_tiles == 1:
                    return TileDanger.SHONPAI_KABE_WEAK
                else:
                    return TileDanger.NON_SHONPAI_KABE_WEAK

        # only consider suji if there is no kabe
        have_suji = [x for x in suji_tiles if tile_34 == x]
        if have_suji:
            if enemy_analyzer.enemy.riichi_tile_136 is not None:
                enemy_riichi_tile_34 = enemy_analyzer.enemy.riichi_tile_136 // 4
                riichi_on_suji = [x for x in suji_tiles if enemy_riichi_tile_34 == x]

                # if it's 2378, then check if riichi was on suji tile
                if simplify(tile_34) <= 2 or simplify(tile_34) >= 6:
                    if 3 <= simplify(enemy_riichi_tile_34) <= 5 and riichi_on_suji:
                        return TileDanger.SUJI_2378_ON_RIICHI
            elif enemy_analyzer.enemy.is_open_hand:
                return TileDanger.SUJI_OPEN_HAND

            return TileDanger.SUJI

        return None

    def _process_danger_for_honor(self, enemy_analyzer, tile_34, number_of_revealed_tiles):
        danger = None
        number_of_yakuhai = enemy_analyzer.enemy.valued_honors.count(tile_34)

        if len(enemy_analyzer.enemy.discards) <= 6:
            if number_of_revealed_tiles == 1:
                if number_of_yakuhai == 0:
                    danger = TileDanger.NON_YAKUHAI_HONOR_SHONPAI_EARLY
                if number_of_yakuhai == 1:
                    danger = TileDanger.YAKUHAI_HONOR_SHONPAI_EARLY
                if number_of_yakuhai == 2:
                    danger = TileDanger.DOUBLE_YAKUHAI_HONOR_SHONPAI_EARLY

            if number_of_revealed_tiles == 2:
                if number_of_yakuhai == 0:
                    danger = TileDanger.NON_YAKUHAI_HONOR_SECOND_EARLY
                if number_of_yakuhai == 1:
                    danger = TileDanger.YAKUHAI_HONOR_SECOND_EARLY
                if number_of_yakuhai == 2:
                    danger = TileDanger.DOUBLE_YAKUHAI_HONOR_SECOND_EARLY
        elif len(enemy_analyzer.enemy.discards) <= 12:
            if number_of_revealed_tiles == 1:
                if number_of_yakuhai == 0:
                    danger = TileDanger.NON_YAKUHAI_HONOR_SHONPAI_MID
                if number_of_yakuhai == 1:
                    danger = TileDanger.YAKUHAI_HONOR_SHONPAI_MID
                if number_of_yakuhai == 2:
                    danger = TileDanger.DOUBLE_YAKUHAI_HONOR_SHONPAI_MID

            if number_of_revealed_tiles == 2:
                if number_of_yakuhai == 0:
                    danger = TileDanger.NON_YAKUHAI_HONOR_SECOND_MID
                if number_of_yakuhai == 1:
                    danger = TileDanger.YAKUHAI_HONOR_SECOND_MID
                if number_of_yakuhai == 2:
                    danger = TileDanger.DOUBLE_YAKUHAI_HONOR_SECOND_MID
        else:
            if number_of_revealed_tiles == 1:
                if number_of_yakuhai == 0:
                    danger = TileDanger.NON_YAKUHAI_HONOR_SHONPAI_LATE
                if number_of_yakuhai == 1:
                    danger = TileDanger.YAKUHAI_HONOR_SHONPAI_LATE
                if number_of_yakuhai == 2:
                    danger = TileDanger.DOUBLE_YAKUHAI_HONOR_SHONPAI_LATE

            if number_of_revealed_tiles == 2:
                if number_of_yakuhai == 0:
                    danger = TileDanger.NON_YAKUHAI_HONOR_SECOND_LATE
                if number_of_yakuhai == 1:
                    danger = TileDanger.YAKUHAI_HONOR_SECOND_LATE
                if number_of_yakuhai == 2:
                    danger = TileDanger.DOUBLE_YAKUHAI_HONOR_SECOND_LATE

        if number_of_revealed_tiles == 3:
            danger = TileDanger.HONOR_THIRD

        return danger

    def _update_discard_candidate(self, tile_34, discard_candidates, player_seat, danger):
        for discard_candidate in discard_candidates:
            if discard_candidate.tile_to_discard_34 == tile_34:
                # we found safe tile, in that case we can ignore all other metrics
                if TileDanger.is_safe(danger):
                    discard_candidate.danger.clear_danger(player_seat)

                # let's put danger metrics to the tile only if we are not yet sure that tile is already safe
                is_known_to_be_safe = (
                    len([x for x in discard_candidate.danger.get_danger_reasons(player_seat) if TileDanger.is_safe(x)])
                    > 0
                )
                if not is_known_to_be_safe:
                    discard_candidate.danger.set_danger(player_seat, danger)

    def is_aidayonken_pattern(self, enemy_analyzer, tile_analyze_34):
        discards = enemy_analyzer.enemy.discards
        discards_34 = [x.value // 4 for x in discards]

        patterns_config = [
            {
                "pattern": [1, 6],
                "danger": [2, 5],
            },
            {
                "pattern": [2, 7],
                "danger": [3, 6],
            },
            {
                "pattern": [3, 8],
                "danger": [4, 7],
            },
            {
                "pattern": [4, 9],
                "danger": [5, 8],
            },
        ]

        for is_suit in [is_pin, is_sou, is_man]:
            if not is_suit(tile_analyze_34):
                continue

            same_suit_simple_discards = []
            for discard_34 in discards_34:
                if is_suit(discard_34):
                    # +1 here to make it easier to read
                    same_suit_simple_discards.append(simplify(discard_34) + 1)

            # +1 here to make it easier to read
            tile_analyze_simplified = simplify(tile_analyze_34) + 1

            for pattern_config in patterns_config:
                has_pattern = (
                    list(set(same_suit_simple_discards) & set(pattern_config["pattern"])) == pattern_config["pattern"]
                )
                if not has_pattern:
                    continue

                has_suji_in_discard = len(list(set(same_suit_simple_discards) & set(pattern_config["danger"]))) != 0
                # we found aidayonken pattern in the discard
                # and aidayonken danger tiles are not in the discard
                # in that case we can increase danger for them
                if not has_suji_in_discard and tile_analyze_simplified in pattern_config["danger"]:
                    return True

        return False

    def _is_matagi_suji(self, enemy_analyzer, tile_analyze_34):
        discards = enemy_analyzer.enemy.discards

        # too early to check matagi suji
        if len(discards) <= 5:
            return False
        # on middle stage check matagi pattern only for one latest discard
        elif len(discards) <= 9:
            latest_discards = [x for x in discards if not x.is_tsumogiri][-1:]
        else:
            # on late stage check matagi pattern for two latest discards
            latest_discards = [x for x in discards if not x.is_tsumogiri][-2:]

        latest_discards_34 = [x.value // 4 for x in latest_discards]
        # make sure that these discards are unique
        latest_discards_34 = list(set(latest_discards_34))

        for enemy_discard_34 in latest_discards_34:
            if not is_tiles_same_suit(enemy_discard_34, tile_analyze_34):
                continue

            # +1 here to make it easier read matagi patterns
            enemy_discard_simplified = simplify(enemy_discard_34) + 1
            tile_analyze_simplified = simplify(tile_analyze_34) + 1

            if enemy_discard_simplified == 2 and tile_analyze_simplified in [1, 4]:
                return True

            if enemy_discard_simplified == 3 and tile_analyze_simplified in [1, 4, 2, 5]:
                return True

            if enemy_discard_simplified == 4 and tile_analyze_simplified in [2, 5, 3, 6]:
                return True

            if enemy_discard_simplified == 5 and tile_analyze_simplified in [3, 6, 4, 7]:
                return True

            if enemy_discard_simplified == 6 and tile_analyze_simplified in [4, 7, 5, 8]:
                return True

            if enemy_discard_simplified == 7 and tile_analyze_simplified in [5, 8, 6, 9]:
                return True

            if enemy_discard_simplified == 8 and tile_analyze_simplified in [6, 9]:
                return True

        return False
