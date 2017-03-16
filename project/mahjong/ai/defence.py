from mahjong.tile import TilesConverter


class Defence(object):
    table = None
    player = None

    def __init__(self, player):
        self.table = player.table
        self.player = player

    def should_go_to_defence_mode(self):
        """
        The method is decides should bot go to the defence mode or not.
        For now only full defence is possible
        :return: true|false
        """
        current_shanten = self.player.ai.previous_shanten

        # if we are in riichi, we can't defence
        if self.player.in_riichi:
            return False

        count_of_riichi_players = 0
        for enemy_player in self.table.enemy_players:
            if enemy_player.in_riichi:
                count_of_riichi_players += 1

        # no one in riichi, we can build our hand
        if count_of_riichi_players == 0:
            return False

        # our hand is far away from tempai, so better to fold
        if current_shanten >= 1:
            return True

        # we are in tempai, let's try to estimate hand value
        hands_estimated_cost = []
        waiting = self.player.ai.waiting
        for tile in waiting:
            hand_result = self.player.ai.estimate_hand_value(tile)
            if hand_result['error'] is None:
                hands_estimated_cost.append(hand_result['cost']['main'])

        # probably we are with opened hand without yaku, let's fold it
        if not hands_estimated_cost:
            return True

        max_cost = max(hands_estimated_cost)
        # our hand in tempai, but it is cheap
        # so we can fold it
        if max_cost < 7000:
            return True

        return False

    def try_to_find_safe_tile_to_discard(self, discard_results):
        threatening_players = self._get_threatening_players()

        if len(threatening_players) > 1:
            safe_tiles = [x.all_safe_tiles for x in threatening_players]
            common_safe_tiles = list(set.intersection(*map(set, safe_tiles)))
            # we found a tile that is safe and common for all threatening players
            if common_safe_tiles:
                result = self._find_tile_to_discard(common_safe_tiles, discard_results)
                if result:
                    return result

        # there are no common safe tiles for all threatening players
        # so let's find most dangerous enemy and let's fold against him
        most_threatening_player = self._get_most_threatening_player(threatening_players)
        safe_tiles = most_threatening_player.all_safe_tiles
        result = self._find_tile_to_discard(safe_tiles, discard_results)
        if result:
            return result

        # we wasn't able to find gembutsu
        return None

    def _find_tile_to_discard(self, safe_tiles, discard_results):
        """
        Try to find most effective tile to discard.
        :param safe_tiles:
        :param discard_results:
        :return: tile in 136 format
        """
        closed_hand = self.player.closed_hand
        closed_hand_34 = TilesConverter.to_34_array(closed_hand)

        # let's check our discard candidates first, maybe we can discard safe tile
        # without ruining our hand
        for safe_tile in safe_tiles:
            for item in discard_results:
                if item.tile_to_discard == safe_tile:
                    return TilesConverter.find_34_tile_in_136_array(safe_tile, closed_hand)

        for safe_tile in safe_tiles:
            for i in range(0, len(closed_hand_34)):
                if closed_hand_34[i] > 0 and i == safe_tile:
                    return TilesConverter.find_34_tile_in_136_array(safe_tile, closed_hand)

    def _get_threatening_players(self):
        """
        For now it is just players in riichi,
        later I will add players with opened valuable hands
        """
        result = []
        for player in self.table.enemy_players:
            if player.in_riichi:
                result.append(player)
        return result

    def _get_most_threatening_player(self, threatening_players):
        """
        For now it will be just a dealer.
        Later I will add discard analyze to find a player with most expensive hand
        """
        for player in threatening_players:
            if player.is_dealer:
                return player

        # dealer is not in threatening players list
        return threatening_players[0]
