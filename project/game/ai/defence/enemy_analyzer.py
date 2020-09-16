from game.ai.defence.yaku_analyzer.honitsu import HonitsuAnalyzer
from game.ai.defence.yaku_analyzer.tanyao import TanyaoAnalyzer
from game.ai.defence.yaku_analyzer.yakuhai import YakuhaiAnalyzer
from game.ai.helpers.possible_forms import PossibleFormsAnalyzer
from mahjong.utils import is_aka_dora, plus_dora
from utils.decisions_constants import DEFENCE_THREATENING_ENEMY
from utils.decisions_logger import DecisionsLogger


class EnemyAnalyzer(object):
    player = None
    possible_forms_analyzer = None

    def __init__(self, player):
        # is enemy
        self.player = player
        self.table = player.table

        # is our bot
        self.main_player = self.table.player
        self.possible_forms_analyzer = PossibleFormsAnalyzer(self.main_player)

    @property
    def is_dealer(self):
        return self.player.is_dealer

    @property
    def all_safe_tiles(self):
        return self.player.all_safe_tiles

    @property
    def in_tempai(self):
        """
        Try to detect is user in tempai or not
        :return: boolean
        """
        # simplest case, user in riichi
        if self.player.in_riichi:
            return True

        if len(self.player.melds) == 4:
            return True

        return False

    @property
    def is_threatening(self):
        """
        Should we fold against this player or not
        :return: boolean
        """
        if self.player.in_riichi:
            DecisionsLogger.debug(DEFENCE_THREATENING_ENEMY, "Enemy in riichi")
            return True

        yaku_analyzers = [
            YakuhaiAnalyzer(self.player),
            TanyaoAnalyzer(self.player),
            HonitsuAnalyzer(self.player),
        ]

        meld_tiles = self.player.meld_tiles
        if meld_tiles:
            dora_count = sum([plus_dora(x, self.table.dora_indicators) for x in meld_tiles])
            # aka dora
            dora_count += sum([1 for x in meld_tiles if is_aka_dora(x, self.table.has_open_tanyao)])

            # enemy has one dora pon/kan
            # and there is 6+ round step
            if len(self.player.melds) == 1 and self.main_player.round_step > 6 and dora_count >= 3:
                DecisionsLogger.debug(
                    DEFENCE_THREATENING_ENEMY,
                    "Enemy has one dora pon/kan and round step is 6+",
                    context={
                        "melds": self.player.melds,
                        "dora_count": dora_count,
                        "round_step": self.main_player.round_step,
                    },
                )

                return True

            melds_han = 0
            active_yaku = []
            for x in yaku_analyzers:
                if x.is_yaku_active():
                    active_yaku.append(x.id)
                    melds_han += x.melds_han()

            if melds_han + dora_count >= 3 and len(self.player.melds) >= 2:
                DecisionsLogger.debug(
                    DEFENCE_THREATENING_ENEMY,
                    "Enemy has 3+ han in open 2+ melds",
                    context={
                        "melds": self.player.melds,
                        "dora_count": dora_count,
                        "melds_han": melds_han,
                        "active_yaku": active_yaku,
                    },
                )

                return True

        return False

    @property
    def assumed_hand_cost(self):
        # FIXME add real value
        return 2000

    @property
    def number_of_unverified_suji(self):
        # FIXME add real value
        return 2

    def total_possible_forms_for_tile(self, tile_34):
        # FIXME: calculating possible forms anew each time is not optimal, we need to cache it somehow
        possible_forms = self.possible_forms_analyzer.calculate_possible_forms(self.all_safe_tiles)
        forms_count = possible_forms[tile_34]

        assert forms_count is not None

        return self.possible_forms_analyzer.calculate_possible_forms_total(forms_count)
