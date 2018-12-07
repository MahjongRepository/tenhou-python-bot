from mahjong.utils import plus_dora, count_tiles_by_suits, is_aka_dora

from game.ai.first_version.defence.yaku_analyzer.yakuhai import YakuhaiAnalyzer
from game.ai.first_version.helpers.possible_forms import PossibleFormsAnalyzer
from utils.decisions_constants import DEFENCE_THREATENING_ENEMY
from utils.decisions_logger import DecisionsLogger


class EnemyAnalyzer(object):
    player = None
    chosen_suit = None

    possible_forms_analyzer = None

    def __init__(self, defence, player):
        self.defence = defence

        # is enemy
        self.player = player
        self.table = player.table
        # is our bot
        self.main_player = self.table.player

        self.chosen_suit = None
        self.possible_forms_analyzer = PossibleFormsAnalyzer(self.player)

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
            DecisionsLogger.debug(
                DEFENCE_THREATENING_ENEMY,
                'Enemy in riichi'
            )
            return True

        discards = self.player.discards
        # discards_34 = TilesConverter.to_34_array([x.value for x in discards])

        # is_honitsu_open_sets, open_hand_suit = False, None
        # is_honitsu_discards, discard_suit = self._is_honitsu_discards(discards_34)

        yaku_analyzers = [
            YakuhaiAnalyzer(self.player)
        ]

        meld_tiles = self.player.meld_tiles
        # meld_tiles_34 = TilesConverter.to_34_array(meld_tiles)
        if meld_tiles:
            dora_count = sum([plus_dora(x, self.table.dora_indicators) for x in meld_tiles])
            # aka dora
            dora_count += sum([1 for x in meld_tiles if is_aka_dora(x, self.table.has_open_tanyao)])

            # enemy has one dora pon/kan
            # and there is 6+ round step
            if len(self.player.melds) == 1 and self.main_player.round_step > 6 and dora_count >= 3:
                DecisionsLogger.debug(
                    DEFENCE_THREATENING_ENEMY,
                    'Enemy has one dora pon/kan and round step is 6+',
                    context={
                        'melds': self.player.melds,
                        'dora_count': dora_count,
                        'round_step': self.main_player.round_step
                    }
                )

                return True

            # enemy has 2+ melds with 2+ doras
            if len(self.player.melds) >= 2 and dora_count >= 2:
                DecisionsLogger.debug(
                    DEFENCE_THREATENING_ENEMY,
                    'Enemy has 2+ melds with 2+ doras',
                    context={
                        'melds': self.player.melds,
                        'dora_count': dora_count
                    }
                )

                return True

            melds_han = 0
            active_yaku = []
            for x in yaku_analyzers:
                if x.is_yaku_active():
                    active_yaku.append(x.id)
                    melds_han += x.melds_han()

            if melds_han + dora_count >= 3 and self.main_player.round_step > 6:
                DecisionsLogger.debug(
                    DEFENCE_THREATENING_ENEMY,
                    'Enemy has 3+ han in open melds and round step is 6+',
                    context={
                        'melds': self.player.melds,
                        'dora_count': dora_count,
                        'melds_han': melds_han,
                        'active_yaku': active_yaku
                    }
                )

                return True

            # check that user has a discard and melds that looks like honitsu
            # is_honitsu_open_sets, open_hand_suit = self._is_honitsu_open_sets(meld_tiles_34)
        #
        # if is_honitsu_open_sets:
        #     for 2 opened melds we had to check discard, to be sure
            # if len(self.player.melds) <= 2 and is_honitsu_discards and discard_suit == open_hand_suit:
            #     self.chosen_suit = open_hand_suit
            #     return True
            #
            # for 3+ opened melds there is no sense to check discard
            # if len(self.player.melds) >= 3:
            #     self.chosen_suit = open_hand_suit
            #     return True

        return False

    @property
    def possible_forms(self):
        return self.possible_forms_analyzer.calculate_possible_forms(self.all_safe_tiles)

    def total_possible_forms_for_tile(self, tile_34):
        # FIXME: calculating possible forms anew each time is not optimal, we need to cache it somehow
        possible_forms = self.possible_forms
        forms_cnt = possible_forms[tile_34]

        assert forms_cnt is not None

        return self.possible_forms_analyzer.calculate_possible_forms_total(forms_cnt)

    def _is_honitsu_open_sets(self, meld_tiles_34):
        """
        Check that user opened all sets with same suit
        :param meld_tiles_34:
        :return:
        """
        total_sets = sum(meld_tiles_34) // 3
        if total_sets < 2:
            return False, None

        result = count_tiles_by_suits(meld_tiles_34)

        suits = [x for x in result if x['name'] != 'honor']
        suits = sorted(suits, key=lambda x: x['count'], reverse=True)

        # for honitsu we can have tiles only in one suit
        if suits[1]['count'] == 0 and suits[2]['count'] == 0:
            return True, suits[0]['function']

        return False, None

    def _is_honitsu_discards(self, discards_34):
        """
        Check that user opened all sets with same suit
        :param discards_34:
        :return:
        """
        total_discards = sum(discards_34)

        # there is no sense to analyze earlier discards
        if total_discards < 6:
            return False, None

        result = count_tiles_by_suits(discards_34)

        honors = [x for x in result if x['name'] == 'honor'][0]
        suits = [x for x in result if x['name'] != 'honor']
        suits = sorted(suits, key=lambda x: x['count'], reverse=False)

        less_suit = suits[0]['count']
        percentage_of_less_suit = (less_suit / total_discards) * 100
        percentage_of_honor_tiles = (honors['count'] / total_discards) * 100

        # there is not too much one suit + honor tiles in the discard
        # so we can tell that user trying to collect honitsu
        if percentage_of_less_suit <= 20 and percentage_of_honor_tiles <= 30:
            return True, suits[0]['function']

        return False, None
