from mahjong.constants import HONOR_INDICES, EAST
from mahjong.tile import TilesConverter
from mahjong.utils import is_man, simplify, is_pin, is_sou, plus_dora


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

        # safe tiles that can be safe based on the table situation
        safe_tiles = self.find_impossible_and_only_pair_waits()

        # first try to check common safe tiles to discard
        if len(threatening_players) > 1:
            common_safe_tiles = [x.all_safe_tiles for x in threatening_players]
            common_safe_tiles = list(set.intersection(*map(set, common_safe_tiles)))
            common_safe_tiles += safe_tiles
            result = self._find_tile_to_discard(common_safe_tiles, discard_results)
            if result:
                return result

        # let's find safe tiles for most dangerous player first
        # and than for all other players if we failed find tile for dangerous player
        for player in threatening_players:
            player_safe_tiles = player.all_safe_tiles + safe_tiles
            result = self._find_tile_to_discard(player_safe_tiles, discard_results)
            if result:
                return result

        # we wasn't able to find gembutsu
        return None

    def find_impossible_and_only_pair_waits(self):
        """
        Impossible waits: fourth honor, fourth 1 man when all 2 man on the table and etc.
        Pair waits: third honor, third 1 man when all 2 man on the table and etc.
        """
        # TODO cache it somehow
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)

        honors = self._find_not_possible_honor_waits(tiles_34)
        kabe = self._find_blocked_by_kabe_waits(tiles_34)

        dead_wait = honors['dead_wait'] + kabe['dead_wait']
        pair_wait = honors['pair_wait'] + kabe['pair_wait']

        # dora is not safe for pair wait, so let's exclude it
        for x in pair_wait:
            if plus_dora(x * 4, self.table.dora_indicators) > 0:
                pair_wait.remove(x)

        return dead_wait + pair_wait

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

        discard_candidates = []
        for safe_tile in safe_tiles:
            for i in range(0, len(closed_hand_34)):
                if closed_hand_34[i] > 0 and i == safe_tile:
                    discard_candidates.append(safe_tile)

        # we wasn't able to find safe tile in our hand
        if not discard_candidates:
            return None

        # results
        final_results = []
        for tile in discard_candidates:
            tiles_34 = TilesConverter.to_34_array(self.player.tiles)
            tiles_34[tile] -= 1
            shanten = self.player.ai.shanten.calculate_shanten(tiles_34,
                                                               self.player.is_open_hand,
                                                               self.player.meld_tiles)
            # tiles_34[tile] += 1
            # print(shanten)

            waiting = []
            for j in range(0, 34):
                tiles_34[j] += 1
                if self.player.ai.shanten.calculate_shanten(tiles_34,
                                                            self.player.is_open_hand,
                                                            self.player.meld_tiles) == shanten - 1:
                    waiting.append(j)
                tiles_34[j] -= 1

            tiles_count = self.player.ai.count_tiles(waiting, tiles_34)

            final_results.append({
                'tile': tile,
                'tiles_count': tiles_count
            })

        # let's find tile that will do less harm to our hand
        final_results = sorted(final_results, key=lambda x: x['tiles_count'], reverse=True)
        tile = final_results[0]['tile']

        return TilesConverter.find_34_tile_in_136_array(tile, closed_hand)

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

    def _suits_tiles(self, tiles_34):
        """
        Return tiles separated by suits
        :param tiles_34:
        :return:
        """
        suits = [
            [0] * 9,
            [0] * 9,
            [0] * 9,
        ]

        for tile in range(0, EAST):
            total_tiles = self.player.total_tiles(tile, tiles_34)
            if not total_tiles:
                continue

            suit_index = None
            simplified_tile = simplify(tile)
            if is_man(tile):
                suit_index = 0
            if is_pin(tile):
                suit_index = 1
            if is_sou(tile):
                suit_index = 2

            suits[suit_index][simplified_tile] += total_tiles

        return suits

    def _find_not_possible_honor_waits(self, tiles_34):
        results = {
            'dead_wait': [],
            'pair_wait': []
        }

        for x in HONOR_INDICES:
            if self.player.total_tiles(x, tiles_34) == 4:
                results['dead_wait'].append(x)

            if self.player.total_tiles(x, tiles_34) == 3:
                results['pair_wait'].append(x)

        return results

    def _find_blocked_by_kabe_waits(self, tiles_34):
        results = {
            'dead_wait': [],
            'pair_wait': []
        }

        # all indices shifted to -1
        kabe_matrix = [
            {'indices': [1], 'blocked_tiles': [0]},
            {'indices': [2], 'blocked_tiles': [0, 1]},
            {'indices': [3], 'blocked_tiles': [1, 2]},
            {'indices': [4], 'blocked_tiles': [2, 6]},
            {'indices': [5], 'blocked_tiles': [6, 7]},
            {'indices': [6], 'blocked_tiles': [7, 8]},
            {'indices': [7], 'blocked_tiles': [8]},
            {'indices': [1, 5], 'blocked_tiles': [3]},
            {'indices': [2, 6], 'blocked_tiles': [4]},
            {'indices': [3, 7], 'blocked_tiles': [5]},
            {'indices': [1, 4], 'blocked_tiles': [2, 3]},
            {'indices': [2, 5], 'blocked_tiles': [3, 4]},
            {'indices': [3, 6], 'blocked_tiles': [4, 5]},
            {'indices': [4, 7], 'blocked_tiles': [5, 6]},
        ]

        # results = []
        suits = self._suits_tiles(tiles_34)
        for x in range(0, 3):
            suit = suits[x]
            # "kabe" - 4 revealed tiles
            kabe_tiles = []
            for y in range(0, 9):
                suit_tile = suit[y]
                if suit_tile == 4:
                    kabe_tiles.append(y)

            blocked_indices = []
            for matrix_item in kabe_matrix:
                all_indices = len(list(set(matrix_item['indices']) - set(kabe_tiles))) == 0
                if all_indices:
                    blocked_indices.extend(matrix_item['blocked_tiles'])

            blocked_indices = list(set(blocked_indices))
            for index in blocked_indices:
                # let's find 34 tile index
                tile = index + x * 9
                if self.player.total_tiles(tile, tiles_34) == 4:
                    results['dead_wait'].append(tile)

                if self.player.total_tiles(tile, tiles_34) == 3:
                    results['pair_wait'].append(tile)

        return results
