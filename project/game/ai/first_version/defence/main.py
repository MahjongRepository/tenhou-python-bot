from mahjong.tile import TilesConverter
from mahjong.utils import plus_dora, is_honor, is_aka_dora

from game.ai.first_version.defence.defence import DefenceTile
from game.ai.first_version.defence.enemy_analyzer import EnemyAnalyzer
from game.ai.first_version.defence.impossible_wait import ImpossibleWait
from game.ai.first_version.defence.kabe import Kabe
from game.ai.first_version.defence.suji import Suji
from game.ai.discard import DiscardOption

import logging
import copy

logger = logging.getLogger("ai")

COUNTER_VALUES = {
    "dealer": 8500,
    "player": 6000,
}

COUNTER_RATIO = {
    "good_shape": [0.33 for i in range(12)] + [0.5 for i in range(12)],
    "bad_shape": [0.66 for i in range(6)] + [0.8 for i in range(6)] + [1 for i in range(12)],
    "pro_good_shape": [0.2 for i in range(25)],
    "pro_bad_shape": [0.33 for i in range(25)],
}

POSITION_RANK = [6, 2, -2, -12]


class DefenceHandler(object):
    table = None
    player = None

    # different strategies
    impossible_wait = None
    kabe = None
    suji = None

    # cached values, that will be used by all strategies
    hand_34 = None
    closed_hand_34 = None

    def __init__(self, player):
        self.table = player.table
        self.player = player

        self.impossible_wait = ImpossibleWait(self)
        self.kabe = Kabe(self)
        self.suji = Suji(self)

        self.hand_34 = None
        self.closed_hand_34 = None

        self.threatening_players = []

    def get_rank_ev(self, hand_value, lose_estimation, win_lose_ratio):
        raw_ranking = [[p.name, p.scores] for p in self.table.get_players_sorted_by_scores()]
        player_name = self.player.name
        enemy_name = ""
        if self.threatening_players:
            enemy_name = self.threatening_players[0].player.name

        # Util function
        def get_position(ranking):
            for i in range(4):
                if player_name == ranking[i][0]:
                    return i

        def get_new_ranking(ranking, name1, name2="", score_diff=0):
            new_ranking = copy.deepcopy(ranking)
            for i in range(4):
                if name1 == ranking[i][0]:
                    new_ranking[i][1] += score_diff
                if name2 == ranking[i][0]:
                    new_ranking[i][1] -= score_diff
            new_ranking.sort(key=lambda x: x[1], reverse=True)
            return new_ranking

        # Get current position
        current_ranking = get_new_ranking(raw_ranking, player_name, score_diff=-4000)
        current_position = get_position(current_ranking)

        # Get estimated position
        ## adjusted ranking which the 4th position +4k
        if self.player.name != raw_ranking[-1][0]:
            adjusted_ranking = get_new_ranking(raw_ranking, raw_ranking[-1][0], score_diff=4000)
        else:
            adjusted_ranking = copy.deepcopy(raw_ranking)
        ## after win
        win_ranking = get_new_ranking(adjusted_ranking, player_name, enemy_name, hand_value)
        win_position = get_position(win_ranking)
        ## after lose
        lose_ranking = get_new_ranking(adjusted_ranking, player_name, enemy_name, -lose_estimation)
        lose_position = get_position(lose_ranking)


        rank_ev = (POSITION_RANK[win_position] - POSITION_RANK[current_position]) + (POSITION_RANK[lose_position] - POSITION_RANK[current_position]) * win_lose_ratio

        return rank_ev

    def should_go_to_defence_mode(self, discard_candidate=None):
        """
        The method is decides should bot go to the defence mode or not.
        For now only full defence is possible
        :return: true|false
        """

        # we drew a tile, so we have 14 tiles in our hand
        if discard_candidate:
            shanten = discard_candidate.shanten
            waiting = discard_candidate.waiting
            wanted_tiles_count = discard_candidate.tiles_count
        # we have 13 tiles in hand (this is not our turn)
        else:
            shanten = self.player.ai.previous_shanten
            waiting = self.player.ai.waiting
            wanted_tiles_count = self.player.ai.wanted_tiles_count

        # if we are the top, it's better to defence
        # if self.player == self.table.get_players_sorted_by_scores()[0] and self.player.scores > 30000:
        #     logger.info("Player is at the 1st position, better to fold.")
        #     return True


        # if we are in riichi or meld too much, we can't defence
        if self.player.in_riichi or self.player.ai.pushing or len(self.player.melds) >= 3:
            logger.info("In reach or pushing state, cannot defence.")
            return False

        # if we are the at the 4st position, it's better to push
        if self.player == self.table.get_players_sorted_by_scores()[-1] and self.table.round_number >= 5:
            logger.info("Player is at the 4st position, better to push.")
            self.player.ai.pushing = True
            self.player.set_state("PUSHING")
            return False

        threatening_players = self._get_threatening_players()
        self.threatening_players = threatening_players  # assign this for further calculation in other methods

        # no one is threatening, so we can build our hand
        if len(threatening_players) == 0:
            return False
        else:
            #logger.info("There are some threatening players! Now shanten is {}".format(shanten))
            pass

        # more than 2 players are threatening, so defense is better
        if len(threatening_players) >= 2:
            logger.info("Watch those players feed each other!")
            return True

        if shanten == 1:
        #     # When player is in 4th position, it's better to push in this situation
        #     if self.player == self.table.get_players_sorted_by_scores()[-1]:
        #         logger.info("Player is in 4th position, better to push.")
        #         return False

            # TODO calculate all possible hand costs for 1-2 shanten
            dora_count = sum([plus_dora(x, self.table.dora_indicators) for x in self.player.tiles])
            # aka dora
            dora_count += sum([1 for x in self.player.tiles if is_aka_dora(x, self.table.has_open_tanyao)])
            # we had 3+ dora in our almost done hand,
            # we can try to push it
            if dora_count >= 3:
                return False

        # our hand is not tempai, so better to fold it
        if shanten != 0:
            #logger.info("Not prepared, ready to fold.")
            return True

        # we are in tempai, let's try to estimate hand value
        hands_estimated_cost = []
        call_riichi = not self.player.is_open_hand
        for tile in waiting:
            # copy of tiles, because we are modifying a list
            tiles = self.player.tiles[:]

            # special case, when we already have 14 tiles in the hand
            if discard_candidate:
                temp_tile = discard_candidate.find_tile_in_hand(self.player.closed_hand)
                tiles.remove(temp_tile)

            hand_result = self.player.ai.estimate_hand_value(tile, tiles, call_riichi)
            if hand_result.error is None:
                hands_estimated_cost.append(hand_result.cost['main'])

        # probably we are with opened hand without yaku, let's fold it
        if not hands_estimated_cost:
            logger.info("This hand cannot win, fold it.")
            return True

        # Get the hand value
        hand_value = sum(hands_estimated_cost) / len(hands_estimated_cost)
        hand_value += self.table.count_of_riichi_sticks * 1000
        if self.player.is_dealer:
            hand_value += 700  # EV for dealer combo
        # EH: makes the calculation of hand value better by adding the remaining tile count

        # Get the shape for attacking
        hand_shape = "bad_shape"
        if wanted_tiles_count > 4:
            hand_shape = "good_shape"

        # Check whether the player is in proactive mode
        if "PROACTIVE" in self.player.play_state:
            hand_shape = "pro_" + hand_shape

        # Get the current hand index
        hand_index = len(self.player.discards)

        # Get the type of threatening player
        counter_player_type = "player"
        if threatening_players[0].is_dealer:
            counter_player_type = "dealer"

        score_ev = hand_value - COUNTER_VALUES[counter_player_type] * COUNTER_RATIO[hand_shape][hand_index]
        rank_ev = self.get_rank_ev(hand_value, COUNTER_VALUES[counter_player_type], COUNTER_RATIO[hand_shape][hand_index])

        should_counter = False

        if self.table.round_number < 3: # DEBUG: set this to 0 to debug rank ev calculation
            # Before Round East 4, use score ev
            if score_ev > 0:
                should_counter = True
        else:
            if rank_ev > 0:
                should_counter = True
            elif rank_ev == 0 and score_ev > 0:
                should_encounter = True


        logger.info(
            '''Cowboy: Counter: 
            Hand Value: {}    Hand Shape: {}    
            Hand Index: {}    Counter Player Type: {}
            Score EV: {}    Rank EV: {} 
            Should Counter: {}'''.format(
                hand_value, hand_shape, hand_index, counter_player_type, score_ev, rank_ev, should_counter))

        if should_counter:
            # set state
            self.player.ai.waiting = waiting
            self.player.ai.wanted_tiles_count = wanted_tiles_count
            if self.player.play_state in ["PREPARING", "DEFENCE"]:
                if hand_shape == "good_shape":
                    self.player.set_state("REACTIVE_GOODSHAPE")
                else:
                    self.player.set_state("REACTIVE_BADSHAPE")

            if self.player != self.table.get_players_sorted_by_scores()[0]:
                # When player is on the top, no need to push, else push it
                self.player.ai.pushing = True

            return False
        else:
            return True

        # our open hand in tempai, but it is cheap
        # so we can fold it
        # if self.player.is_open_hand and max_cost < 7000:
        #    return True

        # when we call riichi we can get ura dora,
        # so it is reasonable to riichi 3k+ hands
        # if not self.player.is_open_hand:
        #     # there are a lot of chances that we will not win with a bad wait
        #     # against other threatening players
        #     if max_cost < 3000 or len(waiting) < 2:
        #         return True

        return False

    def try_to_find_safe_tile_to_discard(self, discard_results):
        self.hand_34 = TilesConverter.to_34_array(self.player.tiles)
        self.closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)

        threatening_players = self._get_threatening_players()

        # safe tiles that can be safe based on the table situation
        safe_tiles = self.impossible_wait.find_tiles_to_discard(threatening_players)

        # first try to check common safe tiles to discard for all players
        if len(threatening_players) > 1:
            against_honitsu = []
            for player in threatening_players:
                if player.chosen_suit:
                    against_honitsu += [self._mark_safe_tiles_against_honitsu(player)]

            common_safe_tiles = [x.all_safe_tiles for x in threatening_players]
            common_safe_tiles += against_honitsu
            # let's find a common tiles that will be safe against all threatening players
            common_safe_tiles = list(set.intersection(*map(set, common_safe_tiles)))
            common_safe_tiles = [DefenceTile(x, DefenceTile.SAFE) for x in common_safe_tiles]

            # there is no sense to calculate suji tiles for honitsu players
            not_honitsu_players = [x for x in threatening_players if x.chosen_suit is None]
            common_suji_tiles = self.suji.find_tiles_to_discard(not_honitsu_players)

            if common_safe_tiles:
                # it can be that safe tile will be mark as "almost safe",
                # but we already have "safe" tile in our hand
                validated_safe_tiles = common_safe_tiles
                for tile in safe_tiles:
                    already_added_tile = [x for x in common_safe_tiles if x.value == tile.value]
                    if not already_added_tile:
                        validated_safe_tiles.append(tile)

                # first try to check 100% safe tiles for all players
                result = self._find_tile_to_discard(validated_safe_tiles, discard_results)
                if result:
                    return result

            if common_suji_tiles:
                # if there is no 100% safe tiles try to check common suji tiles
                result = self._find_tile_to_discard(common_suji_tiles, discard_results)
                if result:
                    return result

        # there are only one threatening player or we wasn't able to find common safe tiles
        # let's find safe tiles for most dangerous player first
        # and than for all other players if we failed find tile for dangerous player
        for player in threatening_players:
            player_safe_tiles = [DefenceTile(x, DefenceTile.SAFE) for x in player.player.all_safe_tiles]
            player_suji_tiles = self.suji.find_tiles_to_discard([player])

            # it can be that safe tile will be mark as "almost safe",
            # but we already have "safe" tile in our hand
            validated_safe_tiles = player_safe_tiles
            for tile in safe_tiles:
                already_added_tile = [x for x in player_safe_tiles if x.value == tile.value]
                if not already_added_tile:
                    validated_safe_tiles.append(tile)

            # better to not use suji for honitsu hands
            if not player.chosen_suit:
                validated_safe_tiles += player_suji_tiles

            result = self._find_tile_to_discard(validated_safe_tiles, discard_results)
            if result:
                return result

            # try to find safe tiles against honitsu
            if player.chosen_suit:
                against_honitsu = self._mark_safe_tiles_against_honitsu(player)
                against_honitsu = [DefenceTile(x, DefenceTile.SAFE) for x in against_honitsu]

                result = self._find_tile_to_discard(against_honitsu, discard_results)
                if result:
                    return result

        # we wasn't able to find safe tile to discard
        logger.info("No safe tiles, try to defence in other ways.")
        logger.info("With such a hand: {}".format(TilesConverter.to_one_line_string(self.player.closed_hand)))
        # find triplets
        for i,c in enumerate(self.closed_hand_34):
            if c >= 3:
                logger.info("Defence with triplets.")
                return DiscardOption(self.player, i, 7, [], 4)

        # find pairs
        for i,c in enumerate(self.closed_hand_34):
            if c >= 2:
                logger.info("Defence with pairs.")
                return DiscardOption(self.player, i, 7, [], 4)

        # find honors
        for i,c in enumerate(self.closed_hand_34[27:]):
            if c >= 1:
                return DiscardOption(self.player, i, 7, [], 4)

        # find 19
        for i,c in enumerate(self.closed_hand_34):
            if i % 9 in [0, 8] and c >= 1:
                return DiscardOption(self.player, i, 7, [], 4)

        # find 28
        for i,c in enumerate(self.closed_hand_34):
            if i % 9 in [1, 7] and c >= 1:
                return DiscardOption(self.player, i, 7, [], 4)

        # we really wasn't able to find safe tile to discard
        logger.info("Really cannot defence.")
        return None

    @property
    def analyzed_enemies(self):
        players = self.player.ai.enemy_players
        return [EnemyAnalyzer(x) for x in players]

    def _find_tile_to_discard(self, safe_tiles, discard_tiles):
        """
        Try to find most effective safe tile to discard
        :param safe_tiles:
        :param discard_tiles:
        :return: DiscardOption
        """
        was_safe_tiles = self._mark_tiles_safety(safe_tiles, discard_tiles)
        if not was_safe_tiles:
            return None

        final_results = sorted(discard_tiles, key=lambda x: (x.danger, x.shanten, -x.tiles_count, x.valuation))

        return final_results[0]

    def _mark_tiles_safety(self, safe_tiles, discard_tiles):
        was_safe_tiles = False
        for safe_tile in safe_tiles:
            for discard_tile in discard_tiles:
                if discard_tile.tile_to_discard == safe_tile.value:
                    was_safe_tiles = True
                    if safe_tile.danger < discard_tile.danger:
                        discard_tile.danger = safe_tile.danger
        return was_safe_tiles

    def _get_threatening_players(self):
        """
        For now it is just players in riichi,
        later I will add players with opened valuable hands.
        Sorted by threat level. Most threatening on the top
        """
        result = []
        for player in self.analyzed_enemies:
            if player.is_threatening:
                result.append(player)

        # dealer is most threatening player
        result = sorted(result, key=lambda x: x.player.is_dealer, reverse=True)

        return result

    def _mark_safe_tiles_against_honitsu(self, player):
        against_honitsu = []
        for tile in range(0, 34):
            if not self.closed_hand_34[tile]:
                continue

            if not player.chosen_suit(tile) and not is_honor(tile):
                against_honitsu.append(tile)
        return against_honitsu


if __name__ == "__main__":
    # Tests
    print(COUNTER_RATIO)
    print(COUNTER_RATIO["bad_shape"][12])
