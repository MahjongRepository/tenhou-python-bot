from mahjong.ai.defence.defence import DefenceTile
from mahjong.ai.defence.impossible_wait import ImpossibleWait
from mahjong.ai.defence.kabe import Kabe
from mahjong.ai.defence.suji import Suji
from mahjong.ai.discard import DiscardOption
from mahjong.tile import TilesConverter


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

        self.closed_hand_34 = None

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
        discard_tiles_34 = [x.tile_to_discard for x in discard_results]
        closed_hand_tiles_34 = [x // 4 for x in self.player.closed_hand]

        self.hand_34 = TilesConverter.to_34_array(self.player.tiles)
        self.closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
        threatening_players = self._get_threatening_players()

        # safe tiles that can be safe based on the table situation
        safe_tiles = self.impossible_wait.find_tiles_to_discard(threatening_players)
        common_suji_tiles = self.suji.find_tiles_to_discard(threatening_players)

        # first try to check common safe tiles to discard for all players
        if len(threatening_players) > 1:
            common_safe_tiles = [x.all_safe_tiles for x in threatening_players]
            common_safe_tiles = list(set.intersection(*map(set, common_safe_tiles)))
            if common_safe_tiles:
                common_safe_tiles = [DefenceTile(x, DefenceTile.SAFE) for x in common_safe_tiles]
                common_safe_tiles += safe_tiles

                # let's check our discard candidates first, maybe we can discard safe tile
                # without ruining our hand
                result = self._find_tile_to_discard(common_safe_tiles, discard_tiles_34)
                if result:
                    return result

                # there are no safe tiles in discard tiles, so let's try to find safe tiles in our hand
                result = self._find_tile_to_discard(common_safe_tiles, closed_hand_tiles_34)
                if result:
                    return result

                # after this lets try to find suji tiles to discard
                result = self._find_tile_to_discard(common_suji_tiles, discard_tiles_34 + closed_hand_tiles_34)
                if result:
                    return result

        # there are only one threatening player or we wasn't able to find common safe tiles
        # let's find safe tiles for most dangerous player first
        # and than for all other players if we failed find tile for dangerous player
        for player in threatening_players:
            player_safe_tiles = [DefenceTile(x, DefenceTile.SAFE) for x in player.all_safe_tiles]
            player_safe_tiles += safe_tiles
            player_suji_tiles = self.suji.find_tiles_to_discard([player])

            # check discard candidates tiles first
            result = self._find_tile_to_discard(player_safe_tiles, discard_tiles_34)
            if result:
                return result

            # check discard candidates and suji tiles
            result = self._find_tile_to_discard(player_suji_tiles, discard_tiles_34)
            if result:
                return result

            # we wasn't able find safe tiles in our discard candidates,
            # so let's check our hand
            result = self._find_tile_to_discard(player_safe_tiles, closed_hand_tiles_34)
            if result:
                return result

            result = self._find_tile_to_discard(player_suji_tiles, closed_hand_tiles_34)
            if result:
                return result

        # we wasn't able to find safe tile to discard
        return None

    def _find_tile_to_discard(self, safe_tiles, tiles):
        """
        Try to find most effective tile to discard.
        :param safe_tiles:
        :param tiles:
        :return: tile in 136 format
        """

        discard_candidates = []
        for safe_tile in safe_tiles:
            for tile in tiles:
                if tile == safe_tile.value:
                    discard_candidates.append(safe_tile)

        # we wasn't able to find safe tile in our hand
        if not discard_candidates:
            return None

        # results
        final_results = []
        for discard_tile in discard_candidates:
            tile = discard_tile.value
            tiles_34 = TilesConverter.to_34_array(self.player.tiles)
            tiles_34[tile] -= 1

            shanten = self.player.ai.shanten.calculate_shanten(tiles_34,
                                                               self.player.is_open_hand,
                                                               self.player.meld_tiles)

            waiting = []
            for j in range(0, 34):
                tiles_34[j] += 1

                if self.player.ai.shanten.calculate_shanten(tiles_34,
                                                            self.player.is_open_hand,
                                                            self.player.meld_tiles) == shanten - 1:
                    waiting.append(j)
                tiles_34[j] -= 1

            tiles_34[tile] += 1

            tiles_count = self.player.ai.count_tiles(waiting, tiles_34)
            final_results.append(DiscardOption(player=self.player,
                                               tile_to_discard=tile,
                                               waiting=waiting,
                                               tiles_count=tiles_count,
                                               danger=discard_tile.danger))

        # let's find tile that will do less harm to our hand
        # and tile that will be maximum safe
        final_results = sorted(final_results, key=lambda x: (-x.danger, x.tiles_count), reverse=True)
        tile = final_results[0].tile_to_discard

        return TilesConverter.find_34_tile_in_136_array(tile, self.player.closed_hand)

    def _get_threatening_players(self):
        """
        For now it is just players in riichi,
        later I will add players with opened valuable hands.
        Sorted by threat level. Most threatening on the top
        """
        result = []
        for player in self.table.enemy_players:
            if player.in_riichi:
                result.append(player)

        # dealer is most threatening player
        result = sorted(result, key=lambda x: x.is_dealer, reverse=True)

        return result
