from copy import copy

from game.ai.defence.yaku_analyzer.honitsu import HonitsuAnalyzer
from game.ai.defence.yaku_analyzer.tanyao import TanyaoAnalyzer
from game.ai.defence.yaku_analyzer.yakuhai import YakuhaiAnalyzer
from game.ai.helpers.defence import EnemyDanger
from game.ai.helpers.possible_forms import PossibleFormsAnalyzer
from mahjong.tile import TilesConverter
from mahjong.utils import is_aka_dora, plus_dora
from utils.general import suits_tiles


class EnemyAnalyzer:
    player = None
    threat_reason = None

    def __init__(self, player):
        self.enemy = player
        self.table = player.table

        # is our bot
        self.main_player = self.table.player
        self.possible_forms_analyzer = PossibleFormsAnalyzer(self.main_player)

    def to_print(self):
        return {"seat": self.enemy.seat, "threat_reason": self.threat_reason}

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
        round_step = self.main_player.round_step

        if self.enemy.in_riichi:
            self._create_danger_reason(EnemyDanger.THREAT_RIICHI, round_step=round_step)
            return True

        melds = self.enemy.melds
        # we can't analyze closed hands for now
        if not melds:
            return False

        yaku_analyzers = [
            YakuhaiAnalyzer(self.enemy),
            TanyaoAnalyzer(self.enemy),
            HonitsuAnalyzer(self.enemy),
        ]

        melds_han = 0
        active_yaku = []
        for x in yaku_analyzers:
            if x.is_yaku_active():
                active_yaku.append(x)
                melds_han += x.melds_han()

        meld_tiles = self.enemy.meld_tiles
        dora_count = sum([plus_dora(x, self.table.dora_indicators) for x in meld_tiles])
        # + aka dora
        dora_count += sum([1 for x in meld_tiles if is_aka_dora(x, self.table.has_open_tanyao)])

        # enemy has one dora pon/kan
        # and there is 6+ round step
        if len(melds) == 1 and round_step > 6 and dora_count >= 3:
            self._create_danger_reason(
                EnemyDanger.THREAT_OPEN_HAND_AND_MULTIPLE_DORA, melds, dora_count, melds_han, active_yaku, round_step
            )
            return True

        if melds_han + dora_count >= 3 and len(melds) >= 2:
            self._create_danger_reason(
                EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND, melds, dora_count, melds_han, active_yaku, round_step
            )
            return True

        return False

    @property
    def assumed_hand_cost(self) -> int:
        """
        How much the hand could cost
        """
        if self.enemy.in_riichi:
            return self._calculate_assumed_hand_cost_for_riichi()
        return self._calculate_assumed_hand_cost()

    @property
    def number_of_unverified_suji(self) -> int:
        maximum_number_of_suji = 18
        verified_suji = 0
        closed_hand_34 = TilesConverter.to_34_array(self.main_player.closed_hand)
        suits = suits_tiles(self.main_player, closed_hand_34)
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

    def get_suji_count_danger_border(self, unverified_suji_count: int) -> int:
        return (10 - unverified_suji_count) * 5

    def _calculate_assumed_hand_cost(self) -> int:
        if self.enemy.is_dealer:
            scale = [1000, 2900, 5800, 7700, 12000, 18000, 18000, 24000, 24000, 48000]
        else:
            scale = [1000, 2000, 3900, 5200, 8000, 12000, 12000, 16000, 16000, 32000]
        han = self.threat_reason.get("dora_count", 0) + self.threat_reason.get("melds_han", 0)
        return scale[han]

    def _calculate_assumed_hand_cost_for_riichi(self) -> int:
        scale_index = 1

        if self.enemy.is_dealer:
            scale = [2900, 5800, 7700, 12000, 18000, 18000, 24000, 24000, 48000]
        else:
            scale = [2000, 3900, 5200, 8000, 12000, 12000, 16000, 16000, 32000]

        # it wasn't early riichi, let's think that it could be more expensive
        if len(self.enemy.discards) > 6:
            scale_index += 1

        total_dora_in_game = len(self.table.dora_indicators) * 4 + (3 * int(self.table.has_aka_dora))
        visible_tiles = TilesConverter.to_136_array(self.table.revealed_tiles) + self.main_player.closed_hand
        visible_dora_tiles = sum([plus_dora(x, self.table.dora_indicators) for x in visible_tiles])
        visible_dora_tiles += sum([int(is_aka_dora(x, self.table.has_aka_dora)) for x in visible_tiles])
        live_dora_tiles = total_dora_in_game - visible_dora_tiles
        assert live_dora_tiles >= 0, "Live dora tiles can't be less than 0"
        # there are too many live dora tiles, let's increase hand cost
        if live_dora_tiles >= 4:
            scale_index += 1

        if scale_index > len(scale):
            scale_index = len(scale)

        return scale[scale_index]

    def _create_danger_reason(
        self, danger_reason, melds=None, dora_count=0, melds_han=0, active_yaku=None, round_step=None
    ):
        danger = copy(danger_reason)
        danger["melds"] = melds
        danger["dora_count"] = dora_count
        danger["melds_han"] = melds_han
        danger["active_yaku"] = active_yaku
        danger["round_step"] = round_step
        danger["number_of_unverified_suji"] = self.number_of_unverified_suji
        danger["suji_count_danger_border"] = self.get_suji_count_danger_border(danger["number_of_unverified_suji"])

        self.threat_reason = danger
        self.threat_reason["assumed_hand_cost"] = self.assumed_hand_cost
