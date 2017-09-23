from mahjong.tile import TilesConverter
from mahjong.utils import plus_dora, count_tiles_by_suits, is_aka_dora


class EnemyAnalyzer(object):
    player = None
    chosen_suit = None
    initialized = False

    def __init__(self, player):
        """
        :param player: instance of EnemyPlayer
        """
        self.player = player
        self.table = player.table

        self.chosen_suit = None

        # we need it to determine user's chosen suit
        self.initialized = self.is_threatening

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
            return True

        discards = self.player.discards
        discards_34 = TilesConverter.to_34_array([x.value for x in discards])

        is_honitsu_open_sets, open_hand_suit = False, None
        is_honitsu_discards, discard_suit = self._is_honitsu_discards(discards_34)

        meld_tiles = self.player.meld_tiles
        meld_tiles_34 = TilesConverter.to_34_array(meld_tiles)
        if meld_tiles:
            dora_count = sum([plus_dora(x, self.table.dora_indicators) for x in meld_tiles])
            # aka dora
            dora_count += sum([1 for x in meld_tiles if is_aka_dora(x, self.table.has_open_tanyao)])
            # enemy has a lot of dora tiles in his opened sets
            # so better to fold against him
            if dora_count >= 3:
                return True

            # check that user has a discard and melds that looks like honitsu
            is_honitsu_open_sets, open_hand_suit = self._is_honitsu_open_sets(meld_tiles_34)

        if is_honitsu_open_sets:
            # for 2 opened melds we had to check discard, to be sure
            if len(self.player.melds) <= 2 and is_honitsu_discards and discard_suit == open_hand_suit:
                self.chosen_suit = open_hand_suit
                return True

            # for 3+ opened melds there is no sense to check discard
            if len(self.player.melds) >= 3:
                self.chosen_suit = open_hand_suit
                return True

        return False

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
