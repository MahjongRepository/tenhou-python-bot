from copy import copy

from game.ai.defence.yaku_analyzer.honitsu import HonitsuAnalyzer
from game.ai.defence.yaku_analyzer.tanyao import TanyaoAnalyzer
from game.ai.defence.yaku_analyzer.yakuhai import YakuhaiAnalyzer
from game.ai.helpers.defence import EnemyDanger
from game.ai.helpers.possible_forms import PossibleFormsAnalyzer
from mahjong.tile import TilesConverter
from mahjong.utils import is_aka_dora, plus_dora


class EnemyAnalyzer:
    player = None
    threat_reason = None

    def __init__(self, player):
        # is enemy
        self.player = player
        self.table = player.table

        # is our bot
        self.main_player = self.table.player
        self.possible_forms_analyzer = PossibleFormsAnalyzer(self.main_player)

    @property
    def in_tempai(self) -> bool:
        """
        Try to detect is user in tempai or not
        """
        # simplest case, user in riichi
        if self.player.in_riichi:
            return True

        if len(self.player.melds) == 4:
            return True

        return False

    @property
    def is_threatening(self) -> bool:
        """
        We are trying to determine other players current threat.
        """
        if self.player.in_riichi:
            self.threat_reason = EnemyDanger.THREAT_RIICHI
            return True

        melds = self.player.melds
        # we can't analyze closed hands for now
        if not melds:
            return False

        yaku_analyzers = [
            YakuhaiAnalyzer(self.player),
            TanyaoAnalyzer(self.player),
            HonitsuAnalyzer(self.player),
        ]

        round_step = self.main_player.round_step
        melds_han = 0
        active_yaku = []
        for x in yaku_analyzers:
            if x.is_yaku_active():
                active_yaku.append(x)
                melds_han += x.melds_han()

        meld_tiles = self.player.meld_tiles
        dora_count = sum([plus_dora(x, self.table.dora_indicators) for x in meld_tiles])
        # + aka dora
        dora_count += sum([1 for x in meld_tiles if is_aka_dora(x, self.table.has_open_tanyao)])

        # enemy has one dora pon/kan
        # and there is 6+ round step
        if len(melds) == 1 and self.main_player.round_step > 6 and dora_count >= 3:
            self.threat_reason = self._create_danger_reason(
                EnemyDanger.THREAT_OPEN_HAND_AND_MULTIPLE_DORA, melds, dora_count, melds_han, active_yaku, round_step
            )
            return True

        if melds_han + dora_count >= 3 and len(melds) >= 2:
            self.threat_reason = self._create_danger_reason(
                EnemyDanger.THREAT_EXPENSIVE_OPEN_HAND, melds, dora_count, melds_han, active_yaku, round_step
            )
            return True

        return False

    def calculate_hand_cost(self) -> int:
        if self.player.in_riichi:
            return self._calculate_assumed_hand_cost_for_riichi()
        return 0

    @property
    def number_of_unverified_suji(self):
        # FIXME add real value
        return 2

    def _calculate_assumed_hand_cost_for_riichi(self) -> int:
        scale_index = 1

        if self.player.is_dealer:
            scale = [2900, 5800, 7700, 12000, 18000, 18000, 24000, 24000, 48000]
        else:
            scale = [2000, 3900, 5200, 8000, 12000, 12000, 16000, 16000, 32000]

        # it wasn't early riichi, let's think that it could be more expensive
        if len(self.player.discards) > 6:
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

    def _create_danger_reason(self, danger_reason, melds, dora_count, melds_han, active_yaku, round_step):
        danger = copy(danger_reason)
        danger["melds"] = melds
        danger["dora_count"] = dora_count
        danger["melds_han"] = melds_han
        danger["active_yaku"] = active_yaku
        danger["round_step"] = round_step
        return danger
