# -*- coding: utf-8 -*-
import math
from functools import reduce

from mahjong.ai.agari import Agari
from mahjong.constants import EAST, SOUTH, WEST, NORTH, CHUN, HATSU, HAKU, TERMINAL_INDICES, HONOR_INDICES
from mahjong.hand_calculating.divider import HandDivider
from mahjong.hand_calculating.fu import HandFuCalculator
from mahjong.hand_calculating.scores import ScoresCalculator
from mahjong.hand_calculating.yaku_config import YakuConfig
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_chi, is_pon, is_pair, is_sou, is_pin, is_man, plus_dora, simplify
from utils.settings_handler import settings


class FinishedHand(object):
    config = YakuConfig()

    def estimate_hand_value(self,
                            tiles,
                            win_tile,
                            is_tsumo=False,
                            is_riichi=False,
                            is_dealer=False,
                            is_ippatsu=False,
                            is_rinshan=False,
                            is_chankan=False,
                            is_haitei=False,
                            is_houtei=False,
                            is_daburu_riichi=False,
                            is_nagashi_mangan=False,
                            is_tenhou=False,
                            is_renhou=False,
                            is_chiihou=False,
                            melds=None,
                            dora_indicators=None,
                            player_wind=None,
                            round_wind=None):
        """
        :param tiles: array with 14 tiles in 136-tile format
        :param win_tile: tile that caused win (ron or tsumo)
        :param is_tsumo:
        :param is_riichi:
        :param is_dealer:
        :param is_ippatsu:
        :param is_rinshan:
        :param is_chankan:
        :param is_haitei:
        :param is_houtei:
        :param is_tenhou:
        :param is_renhou:
        :param is_chiihou:
        :param is_daburu_riichi:
        :param is_nagashi_mangan:
        :param melds: array with Meld objects
        :param dora_indicators: array of tiles in 136-tile format
        :param player_wind: index of player wind
        :param round_wind: index of round wind
        :return: The dictionary with hand cost or error response

        {"cost": {'main': 1000, 'additional': 0}, "han": 1, "fu": 30, "error": None, "hand_yaku": []}
        {"cost": None, "han": 0, "fu": 0, "error": "Hand is not valid", "hand_yaku": []}
        """

        if not melds:
            melds = []

        opened_melds = [x for x in melds if x.opened]
        is_open_hand = len(opened_melds) > 0

        # TODO Deprecated. Change it to melds in all places
        called_kan_indices = []
        kan_indices_136 = []
        for meld in melds:
            if meld.type == Meld.KAN or meld.type == Meld.CHANKAN:
                called_kan_indices.append(meld.tiles[0] // 4)
                kan_indices_136 = [meld.tiles[0]]

        open_sets_34 = []
        for meld in opened_melds:
            open_sets_34.append([x // 4 for x in meld.tiles[:3]])

        if not dora_indicators:
            dora_indicators = []

        agari = Agari()
        cost = None
        error = None
        hand_yaku = []
        han = 0
        fu = 0
        scores_calculator = ScoresCalculator()

        def return_response():
            return {'cost': cost, 'error': error, 'han': han, 'fu': fu, 'hand_yaku': hand_yaku}

        # special situation
        if is_nagashi_mangan:
            hand_yaku.append(self.config.nagashi_mangan)
            fu = 30
            han = self.config.nagashi_mangan.han_closed
            cost = scores_calculator.calculate_scores(han, fu, is_tsumo, is_dealer)
            return return_response()

        if win_tile not in tiles:
            error = "Win tile not in the hand"
            return return_response()

        if is_riichi and is_open_hand:
            error = "Riichi can't be declared with open hand"
            return return_response()

        if is_ippatsu and is_open_hand:
            error = "Ippatsu can't be declared with open hand"
            return return_response()

        if is_ippatsu and not is_riichi and not is_daburu_riichi:
            error = "Ippatsu can't be declared without riichi"
            return return_response()

        tiles_34 = TilesConverter.to_34_array(tiles)
        divider = HandDivider()
        fu_calculator = HandFuCalculator()

        if not agari.is_agari(tiles_34, open_sets_34):
            error = 'Hand is not winning'
            return return_response()

        hand_options = divider.divide_hand(tiles_34, open_sets_34, called_kan_indices)

        calculated_hands = []
        for hand in hand_options:
            cost = None
            error = None
            hand_yaku = []
            han = 0
            fu = 0

            if is_tsumo or is_open_hand:
                fu += 20
            else:
                fu += 30

            pon_sets = [x for x in hand if is_pon(x)]
            chi_sets = [x for x in hand if is_chi(x)]
            additional_fu = fu_calculator.calculate_additional_fu(win_tile,
                                                                  hand,
                                                                  is_tsumo,
                                                                  player_wind,
                                                                  round_wind,
                                                                  open_sets_34,
                                                                  called_kan_indices)

            if additional_fu == 0 and len(chi_sets) == 4:
                """
                - A hand without pon and kan sets, so it should contains all sequences and a pair
                - The pair should be not valued
                - The waiting must be an open wait (on 2 different tiles)
                - Hand should be closed
                """
                if is_open_hand:
                    fu += 2
                    is_pinfu = False
                else:
                    is_pinfu = True
            else:
                fu += additional_fu
                is_pinfu = False

            if is_tsumo:
                if not is_open_hand:
                    hand_yaku.append(self.config.tsumo)

                # pinfu + tsumo always is 20 fu
                if not is_pinfu:
                    fu += 2

            if is_pinfu:
                hand_yaku.append(self.config.pinfu)

            is_chitoitsu = self.is_chitoitsu(hand)
            # let's skip hand that looks like chitoitsu, but it contains open sets
            if is_chitoitsu and is_open_hand:
                continue

            if is_chitoitsu:
                hand_yaku.append(self.config.chiitoitsu)

            is_tanyao = self.config.tanyao.is_condition_met(hand)
            if is_open_hand and not settings.OPEN_TANYAO:
                is_tanyao = False

            if is_tanyao:
                hand_yaku.append(self.config.tanyao)

            if is_riichi and not is_daburu_riichi:
                hand_yaku.append(self.config.riichi)

            if is_daburu_riichi:
                hand_yaku.append(self.config.daburu_riichi)

            if is_ippatsu:
                hand_yaku.append(self.config.ippatsu)

            if is_rinshan:
                hand_yaku.append(self.config.rinshan)

            if is_chankan:
                hand_yaku.append(self.config.chankan)

            if is_haitei:
                hand_yaku.append(self.config.haitei)

            if is_houtei:
                hand_yaku.append(self.config.houtei)

            if is_renhou:
                hand_yaku.append(self.config.renhou)

            if is_tenhou:
                hand_yaku.append(self.config.tenhou)

            if is_chiihou:
                hand_yaku.append(self.config.chiihou)

            if self.config.honitsu.is_condition_met(hand):
                hand_yaku.append(self.config.honitsu)

            if self.config.chinitsu.is_condition_met(hand):
                hand_yaku.append(self.config.chinitsu)

            if self.is_tsuisou(hand):
                hand_yaku.append(self.config.tsuisou)

            if self.config.honroto.is_condition_met(hand):
                hand_yaku.append(self.config.honroto)

            if self.is_chinroto(hand):
                hand_yaku.append(self.config.chinroto)

            # small optimization, try to detect yaku with chi required sets only if we have chi sets in hand
            if len(chi_sets):
                if self.config.chanta.is_condition_met(hand):
                    hand_yaku.append(self.config.chanta)

                if self.config.junchan.is_condition_met(hand):
                    hand_yaku.append(self.config.junchan)

                if self.config.ittsu.is_condition_met(hand):
                    hand_yaku.append(self.config.ittsu)

                if not is_open_hand:
                    if self.config.ryanpeiko.is_condition_met(hand):
                        hand_yaku.append(self.config.ryanpeiko)
                    elif self.config.iipeiko.is_condition_met(hand):
                        hand_yaku.append(self.config.iipeiko)

                if self.config.sanshoku.is_condition_met(hand):
                    hand_yaku.append(self.config.sanshoku)

            # small optimization, try to detect yaku with pon required sets only if we have pon sets in hand
            if len(pon_sets):
                if self.config.toitoi.is_condition_met(hand):
                    hand_yaku.append(self.config.toitoi)

                if self.config.sanankou.is_condition_met(hand, win_tile, open_sets_34, is_tsumo):
                    hand_yaku.append(self.config.sanankou)

                if self.config.sanshoku_douko.is_condition_met(hand):
                    hand_yaku.append(self.config.sanshoku_douko)

                if self.config.shosangen.is_condition_met(hand):
                    hand_yaku.append(self.config.shosangen)

                if self.config.haku.is_condition_met(hand):
                    hand_yaku.append(self.config.haku)

                if self.config.hatsu.is_condition_met(hand):
                    hand_yaku.append(self.config.hatsu)

                if self.config.chun.is_condition_met(hand):
                    hand_yaku.append(self.config.hatsu)

                if self.is_east(hand, player_wind, round_wind):
                    if player_wind == EAST:
                        hand_yaku.append(self.config.yakuhai_place)

                    if round_wind == EAST:
                        hand_yaku.append(self.config.yakuhai_round)

                if self.is_south(hand, player_wind, round_wind):
                    if player_wind == SOUTH:
                        hand_yaku.append(self.config.yakuhai_place)

                    if round_wind == SOUTH:
                        hand_yaku.append(self.config.yakuhai_round)

                if self.is_west(hand, player_wind, round_wind):
                    if player_wind == WEST:
                        hand_yaku.append(self.config.yakuhai_place)

                    if round_wind == WEST:
                        hand_yaku.append(self.config.yakuhai_round)

                if self.is_north(hand, player_wind, round_wind):
                    if player_wind == NORTH:
                        hand_yaku.append(self.config.yakuhai_place)

                    if round_wind == NORTH:
                        hand_yaku.append(self.config.yakuhai_round)

                if self.is_daisangen(hand):
                    hand_yaku.append(self.config.daisangen)

                if self.is_shosuushi(hand):
                    hand_yaku.append(self.config.shosuushi)

                if self.is_daisuushi(hand):
                    hand_yaku.append(self.config.daisuushi)

                if self.is_ryuisou(hand):
                    hand_yaku.append(self.config.ryuisou)

                if not is_open_hand and self.is_chuuren_poutou(hand):
                    if tiles_34[win_tile // 4] == 2:
                        hand_yaku.append(self.config.daburu_chuuren_poutou)
                    else:
                        hand_yaku.append(self.config.chuuren_poutou)

                if not is_open_hand and self.is_suuankou(win_tile, hand, is_tsumo):
                    if tiles_34[win_tile // 4] == 2:
                        hand_yaku.append(self.config.suuankou_tanki)
                    else:
                        hand_yaku.append(self.config.suuankou)

                if self.is_sankantsu(melds):
                    hand_yaku.append(self.config.sankantsu)

                if self.is_suukantsu(melds):
                    hand_yaku.append(self.config.suukantsu)

            # chitoitsu is always 25 fu
            if is_chitoitsu:
                fu = 25

            # yakuman is not connected with other yaku
            yakuman_list = [x for x in hand_yaku if x.is_yakuman]
            if yakuman_list:
                hand_yaku = yakuman_list

            # calculate han
            for item in hand_yaku:
                if is_open_hand and item.han_open:
                    han += item.han_open
                else:
                    han += item.han_closed

            # round up
            # 22 -> 30 and etc.
            if fu != 25:
                fu = int(math.ceil(fu / 10.0)) * 10

            if han == 0 or (han == 1 and fu < 30):
                error = 'Not valid han ({0}) and fu ({1})'.format(han, fu)
                cost = None
            # else:

            # we can add dora han only if we have other yaku in hand
            # and if we don't have yakuman
            if not yakuman_list:
                tiles_for_dora = tiles + kan_indices_136
                count_of_dora = 0
                count_of_aka_dora = 0
                for tile in tiles_for_dora:
                    count_of_dora += plus_dora(tile, dora_indicators)

                if count_of_dora:
                    yaku_item = self.config.dora
                    yaku_item.han_open = count_of_dora
                    yaku_item.han_closed = count_of_dora
                    hand_yaku.append(yaku_item)
                    han += count_of_dora

                if count_of_aka_dora:
                    yaku_item = self.config.aka_dora
                    yaku_item.han_open = count_of_aka_dora
                    yaku_item.han_closed = count_of_aka_dora
                    hand_yaku.append(yaku_item)
                    han += count_of_aka_dora

            if not error:
                cost = scores_calculator.calculate_scores(han, fu, is_tsumo, is_dealer)

            calculated_hand = {
                'cost': cost,
                'error': error,
                'hand_yaku': hand_yaku,
                'han': han,
                'fu': fu
            }
            calculated_hands.append(calculated_hand)

        # exception hand
        if not is_open_hand and self.is_kokushi(tiles_34):
            if tiles_34[win_tile // 4] == 2:
                han = self.config.daburu_kokushi.han_closed
            else:
                han = self.config.kokushi.han_closed
            fu = 0
            cost = scores_calculator.calculate_scores(han, fu, is_tsumo, is_dealer)
            calculated_hands.append({
                'cost': cost,
                'error': None,
                'hand_yaku': [self.config.kokushi],
                'han': han,
                'fu': fu
            })

        # let's use cost for most expensive hand
        calculated_hands = sorted(calculated_hands, key=lambda x: (x['han'], x['fu']), reverse=True)

        calculated_hand = calculated_hands[0]
        cost = calculated_hand['cost']
        error = calculated_hand['error']
        hand_yaku = calculated_hand['hand_yaku']
        han = calculated_hand['han']
        fu = calculated_hand['fu']

        return return_response()

    def is_chitoitsu(self, hand):
        """
        Hand contains only pairs
        :param hand: list of hand's sets
        :return: boolean
        """
        return len(hand) == 7

    def is_sankantsu(self, melds):
        """
        The hand with three kan sets
        :param melds: array of Meld objects
        :return: boolean
        """
        kan_sets = [x for x in melds if x.type == Meld.KAN]
        return len(kan_sets) == 3

    def is_east(self, hand, player_wind, round_wind):
        """
        Pon of east winds
        :param hand: list of hand's sets
        :param player_wind: index of player wind
        :param round_wind: index of round wind
        :return: boolean
        """

        if len([x for x in hand if is_pon(x) and x[0] == player_wind]) == 1 and player_wind == EAST:
            return True

        if len([x for x in hand if is_pon(x) and x[0] == round_wind]) == 1 and round_wind == EAST:
            return True

        return False

    def is_south(self, hand, player_wind, round_wind):
        """
        Pon of south winds
        :param hand: list of hand's sets
        :param player_wind: index of player wind
        :param round_wind: index of round wind
        :return: boolean
        """

        if len([x for x in hand if is_pon(x) and x[0] == player_wind]) == 1 and player_wind == SOUTH:
            return True

        if len([x for x in hand if is_pon(x) and x[0] == round_wind]) == 1 and round_wind == SOUTH:
            return True

        return False

    def is_west(self, hand, player_wind, round_wind):
        """
        Pon of west winds
        :param hand: list of hand's sets
        :param player_wind: index of player wind
        :param round_wind: index of round wind
        :return: boolean
        """

        if len([x for x in hand if is_pon(x) and x[0] == player_wind]) == 1 and player_wind == WEST:
            return True

        if len([x for x in hand if is_pon(x) and x[0] == round_wind]) == 1 and round_wind == WEST:
            return True

        return False

    def is_north(self, hand, player_wind, round_wind):
        """
        Pon of north winds
        :param hand: list of hand's sets
        :param player_wind: index of player wind
        :param round_wind: index of round wind
        :return: boolean
        """

        if len([x for x in hand if is_pon(x) and x[0] == player_wind]) == 1 and player_wind == NORTH:
            return True

        if len([x for x in hand if is_pon(x) and x[0] == round_wind]) == 1 and round_wind == NORTH:
            return True

        return False

    def is_daisangen(self, hand):
        """
        The hand contains three sets of dragons
        :param hand: list of hand's sets
        :return: boolean
        """
        count_of_dragon_pon_sets = 0
        for item in hand:
            if is_pon(item) and item[0] in [CHUN, HAKU, HATSU]:
                count_of_dragon_pon_sets += 1
        return count_of_dragon_pon_sets == 3

    def is_shosuushi(self, hand):
        """
        The hand contains three sets of winds and a pair of the remaining wind.
        :param hand: list of hand's sets
        :return: boolean
        """
        pon_sets = [x for x in hand if is_pon(x)]
        if len(pon_sets) < 3:
            return False

        count_of_wind_sets = 0
        wind_pair = 0
        winds = [EAST, SOUTH, WEST, NORTH]
        for item in hand:
            if is_pon(item) and item[0] in winds:
                count_of_wind_sets += 1

            if is_pair(item) and item[0] in winds:
                wind_pair += 1

        return count_of_wind_sets == 3 and wind_pair == 1

    def is_daisuushi(self, hand):
        """
        The hand contains four sets of winds
        :param hand: list of hand's sets
        :return: boolean
        """
        pon_sets = [x for x in hand if is_pon(x)]
        if len(pon_sets) != 4:
            return False

        count_wind_sets = 0
        winds = [EAST, SOUTH, WEST, NORTH]
        for item in pon_sets:
            if is_pon(item) and item[0] in winds:
                count_wind_sets += 1

        return count_wind_sets == 4

    def is_tsuisou(self, hand):
        """
        Hand composed entirely of honour tiles.
        :param hand: list of hand's sets
        :return: boolean
        """
        indices = reduce(lambda z, y: z + y, hand)
        return all(x in HONOR_INDICES for x in indices)

    def is_chinroto(self, hand):
        """
        Hand composed entirely of terminal tiles.
        :param hand: list of hand's sets
        :return: boolean
        """
        indices = reduce(lambda z, y: z + y, hand)
        return all(x in TERMINAL_INDICES for x in indices)

    def is_kokushi(self, tiles_34):
        """
        A hand composed of one of each of the terminals and honour tiles plus
        any tile that matches anything else in the hand.
        :param tiles_34:
        :return: boolean
        """
        if (tiles_34[0] * tiles_34[8] * tiles_34[9] * tiles_34[17] * tiles_34[18] *
                tiles_34[26] * tiles_34[27] * tiles_34[28] * tiles_34[29] * tiles_34[30] *
                tiles_34[31] * tiles_34[32] * tiles_34[33] == 2):
            return True

    def is_ryuisou(self, hand):
        """
        Hand composed entirely of green tiles. Green tiles are: green dragons and 2, 3, 4, 6 and 8 of sou.
        :param hand: list of hand's sets
        :return: boolean
        """
        green_indices = [19, 20, 21, 23, 25, HATSU]
        indices = reduce(lambda z, y: z + y, hand)
        return all(x in green_indices for x in indices)

    def is_suuankou(self, win_tile, hand, is_tsumo):
        """
        Four closed pon sets
        :param win_tile: 136 tiles format
        :param hand: list of hand's sets
        :param is_tsumo:
        :return: boolean
        """
        win_tile //= 4
        closed_hand = []
        for item in hand:
            # if we do the ron on syanpon wait our pon will be consider as open
            if is_pon(item) and win_tile in item and not is_tsumo:
                continue

            closed_hand.append(item)

        count_of_pon = len([i for i in closed_hand if is_pon(i)])
        return count_of_pon == 4

    def is_chuuren_poutou(self, hand):
        """
        The hand contains 1-1-1-2-3-4-5-6-7-8-9-9-9 of one suit, plus any other tile of the same suit.
        :param hand: list of hand's sets
        :return: boolean
        """

        sou_sets = 0
        pin_sets = 0
        man_sets = 0
        honor_sets = 0
        for item in hand:
            if is_sou(item[0]):
                sou_sets += 1
            elif is_pin(item[0]):
                pin_sets += 1
            elif is_man(item[0]):
                man_sets += 1
            else:
                honor_sets += 1

        sets = [sou_sets, pin_sets, man_sets]
        only_one_suit = len([x for x in sets if x != 0]) == 1
        if not only_one_suit or honor_sets > 0:
            return False

        indices = reduce(lambda z, y: z + y, hand)
        # cast tile indices to 0..8 representation
        indices = [simplify(x) for x in indices]

        # 1-1-1
        if len([x for x in indices if x == 0]) < 3:
            return False

        # 9-9-9
        if len([x for x in indices if x == 8]) < 3:
            return False

        # 1-2-3-4-5-6-7-8-9 and one tile to any of them
        indices.remove(0)
        indices.remove(0)
        indices.remove(8)
        indices.remove(8)
        for x in range(0, 9):
            if x in indices:
                indices.remove(x)

        if len(indices) == 1:
            return True

        return False

    def is_suukantsu(self, melds):
        """
        The hand with four kan sets
        :param melds: array of Meld objects
        :return: boolean
        """
        kan_sets = [x for x in melds if x.type == Meld.KAN]
        return len(kan_sets) == 4

