from copy import copy

from game.ai.defence.yaku_analyzer.atodzuke import AtodzukeAnalyzer
from game.ai.defence.yaku_analyzer.chinitsu import ChinitsuAnalyzer
from game.ai.defence.yaku_analyzer.honitsu import HonitsuAnalyzer
from game.ai.defence.yaku_analyzer.tanyao import TanyaoAnalyzer
from game.ai.defence.yaku_analyzer.toitoi import ToitoiAnalyzer
from game.ai.defence.yaku_analyzer.yakuhai import YakuhaiAnalyzer
from game.ai.helpers.defence import EnemyDanger, TileDanger
from game.ai.helpers.possible_forms import PossibleFormsAnalyzer
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor, plus_dora
from utils.general import separate_tiles_by_suits


class EnemyAnalyzer:
    player = None
    threat_reason = None

    def __init__(self, player):
        self.enemy = player
        self.table = player.table

        # is our bot
        self.main_player = self.table.player
        self.possible_forms_analyzer = PossibleFormsAnalyzer(self.main_player)

    def serialize(self):
        return {"seat": self.enemy.seat, "threat_reason": self.threat_reason}

    @property
    def enemy_discards_until_all_tsumogiri(self):
        """
        Return all enemy discards including the last one from the hand but not further
        """
        discards = self.enemy.discards

        if not discards:
            return []

        discards_from_hand = [x for x in discards if not x.is_tsumogiri]
        if not discards_from_hand:
            return []

        last_from_hand = discards_from_hand[-1]
        index_of_last_from_hand = discards.index(last_from_hand)

        return discards[: index_of_last_from_hand + 1]

    @property
    def in_tempai(self) -> bool:
        """
        Try to detect is user in tempai or not
        """
        # simplest case, user in riichi
        if self.enemy.in_riichi:
            return True

        if len(self.enemy.melds) == 4:
            return True

        return False

    @property
    def is_threatening(self) -> bool:
        """
        We are trying to determine other players current threat
        """
        round_step = len(self.enemy.discards)

        if self.enemy.in_riichi:
            self._create_danger_reason(EnemyDanger.THREAT_RIICHI, round_step=round_step)
            return True

        melds = self.enemy.melds
        # we can't analyze closed hands for now
        if not melds:
            return False

        active_yaku = []
        sure_han = 0

        yakuhai_analyzer = YakuhaiAnalyzer(self.enemy)
        if yakuhai_analyzer.is_yaku_active():
            active_yaku.append(yakuhai_analyzer)
            sure_han = yakuhai_analyzer.melds_han()

        yaku_analyzers = [
            ChinitsuAnalyzer(self.enemy),
            HonitsuAnalyzer(self.enemy),
            ToitoiAnalyzer(self.enemy),
            TanyaoAnalyzer(self.enemy),
        ]

        for x in yaku_analyzers:
            if x.is_yaku_active():
                active_yaku.append(x)

        if not active_yaku:
            active_yaku.append(AtodzukeAnalyzer(self.enemy))
            sure_han = 1

        # FIXME: probably our approach here should be refactored and we should not care about cost
        if not sure_han:
            main_yaku = [x for x in active_yaku if not x.is_absorbed(active_yaku)]
            if main_yaku:
                sure_han = main_yaku[0].melds_han()
            else:
                sure_han = 1

        meld_tiles = self.enemy.meld_tiles
        dora_count = sum(
            [plus_dora(x, self.table.dora_indicators, add_aka_dora=self.table.has_aka_dora) for x in meld_tiles]
        )
        sure_han += dora_count

        if len(melds) == 1 and round_step > 5 and sure_han >= 4:
            self._create_danger_reason(
                EnemyDanger.THREAT_OPEN_HAND_AND_MULTIPLE_DORA, melds, dora_count, active_yaku, round_step
            )
            return True

        if len(melds) >= 2 and round_step > 4 and sure_han >= 3:
            self._create_danger_reason(
                EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND, melds, dora_count, active_yaku, round_step
            )
            return True

        if len(melds) >= 1 and round_step > 10 and sure_han >= 2 and self.enemy.is_dealer:
            self._create_danger_reason(
                EnemyDanger.THREAT_OPEN_HAND_UNKNOWN_COST, melds, dora_count, active_yaku, round_step
            )
            return True

        # we are not sure how expensive this is, but let's be a little bit careful
        if (round_step > 14 and len(melds) >= 1) or (round_step > 9 and len(melds) >= 2) or len(melds) >= 3:
            self._create_danger_reason(
                EnemyDanger.THREAT_OPEN_HAND_UNKNOWN_COST, melds, dora_count, active_yaku, round_step
            )
            return True

        return False

    def get_melds_han(self, tile_34) -> int:
        melds_han = 0

        for yaku_analyzer in self.threat_reason["active_yaku"]:
            if not (tile_34 in yaku_analyzer.get_safe_tiles_34()) and not yaku_analyzer.is_absorbed(
                self.threat_reason["active_yaku"], tile_34
            ):
                melds_han += yaku_analyzer.melds_han() * yaku_analyzer.get_tempai_probability_modifier()

        return int(melds_han)

    def get_assumed_hand_cost(self, tile_136) -> int:
        """
        How much the hand could cost
        """
        if self.enemy.in_riichi:
            return self._calculate_assumed_hand_cost_for_riichi(tile_136)
        return self._calculate_assumed_hand_cost(tile_136)

    @property
    def number_of_unverified_suji(self) -> int:
        maximum_number_of_suji = 18
        verified_suji = 0
        suits = separate_tiles_by_suits(TilesConverter.to_34_array([x * 4 for x in self.enemy.all_safe_tiles]))
        for suit in suits:
            # indices started from 0
            suji_indices = [[0, 3, 6], [1, 4, 7], [2, 5, 8]]
            for suji in suji_indices:
                if suit[suji[0]] and suit[suji[2]]:
                    verified_suji += 2
                elif suit[suji[0]] or suit[suji[2]]:
                    verified_suji += 1
                    if suit[suji[1]]:
                        verified_suji += 1
                elif suit[suji[1]]:
                    verified_suji += 2
        result = maximum_number_of_suji - verified_suji
        assert result >= 0, "number of unverified suji can't be less than 0"
        return result

    @property
    def unverified_suji_coeff(self) -> int:
        return self.calculate_suji_count_coeff(self.number_of_unverified_suji)

    @staticmethod
    def calculate_suji_count_coeff(unverified_suji_count: int) -> int:
        return (TileDanger.SUJI_COUNT_BOUNDARY - unverified_suji_count) * TileDanger.SUJI_COUNT_MODIFIER

    def _get_dora_scale_bonus(self, tile_136):
        tile_34 = tile_136 // 4
        scale_bonus = 0

        dora_count = plus_dora(tile_136, self.table.dora_indicators, add_aka_dora=self.table.has_aka_dora)

        if is_honor(tile_34):
            closed_hand_34 = TilesConverter.to_34_array(self.main_player.closed_hand)
            revealed_tiles = self.main_player.number_of_revealed_tiles(tile_34, closed_hand_34)
            if revealed_tiles < 2:
                scale_bonus += dora_count * 3
            else:
                scale_bonus += dora_count * 2
        else:
            scale_bonus += dora_count

        return scale_bonus

    def _calculate_assumed_hand_cost(self, tile_136) -> int:
        tile_34 = tile_136 // 4

        melds_han = self.get_melds_han(tile_34)
        if melds_han == 0:
            return 0

        han = melds_han
        han += self.threat_reason.get("dora_count", 0)
        han += self._get_dora_scale_bonus(tile_136)

        if self.enemy.is_dealer:
            scale = [1000, 2900, 5800, 12000, 12000, 18000, 18000, 24000, 24000, 24000, 36000, 36000, 48000]
        else:
            scale = [1000, 2000, 3900, 8000, 8000, 12000, 12000, 16000, 16000, 16000, 24000, 24000, 32000]

        if han > len(scale) - 1:
            han = len(scale) - 1
        elif han == 0:
            han = 1

        return scale[han - 1]

    def _calculate_assumed_hand_cost_for_riichi(self, tile_136) -> int:
        scale_index = 0

        if self.enemy.is_dealer:
            scale = [2900, 5800, 7700, 12000, 12000, 18000, 18000, 24000, 24000, 48000]
        else:
            scale = [2000, 3900, 5200, 8000, 8000, 12000, 12000, 16000, 16000, 32000]

        # it wasn't early riichi, let's think that it could be more expensive
        if 6 < len(self.enemy.discards) <= 12:
            scale_index += 1

        # more late riichi, probably means more expensive riichi
        if len(self.enemy.discards) > 12:
            scale_index += 2

        if self.enemy.is_ippatsu:
            scale_index += 1

        total_dora_in_game = len(self.table.dora_indicators) * 4 + (3 * int(self.table.has_aka_dora))
        visible_tiles = self.table.revealed_tiles_136 + self.main_player.closed_hand
        visible_dora_tiles = sum(
            [plus_dora(x, self.table.dora_indicators, add_aka_dora=self.table.has_aka_dora) for x in visible_tiles]
        )
        live_dora_tiles = total_dora_in_game - visible_dora_tiles
        assert live_dora_tiles >= 0, "Live dora tiles can't be less than 0"
        # there are too many live dora tiles, let's increase hand cost
        if live_dora_tiles >= 4:
            scale_index += 1

        # if we are discarding dora we are obviously going to make enemy hand more expensive
        scale_index += self._get_dora_scale_bonus(tile_136)

        # if enemy has closed kan, his hand is more expensive on average
        for meld in self.enemy.melds:
            # if he is in riichi he can only have closed kan
            assert meld.type == Meld.KAN and not meld.opened

            # plus two just because of riichi with kan
            scale_index += 2

            # higher danger for doras
            for tile in meld.tiles:
                scale_index += plus_dora(tile, self.table.dora_indicators, add_aka_dora=self.table.has_aka_dora)

            # higher danger for yakuhai
            tile_34 = meld.tiles[0] // 4
            scale_index += len([x for x in self.enemy.valued_honors if x == tile_34])

        if scale_index > len(scale) - 1:
            scale_index = len(scale) - 1

        return scale[scale_index]

    def _create_danger_reason(self, danger_reason, melds=None, dora_count=0, active_yaku=None, round_step=None):
        new_danger_reason = copy(danger_reason)
        new_danger_reason["melds"] = melds
        new_danger_reason["dora_count"] = dora_count
        new_danger_reason["active_yaku"] = active_yaku
        new_danger_reason["round_step"] = round_step

        self.threat_reason = new_danger_reason
