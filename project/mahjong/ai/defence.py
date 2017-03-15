from mahjong.tile import Tile, TilesConverter


class PlayerMeta(object):
    seat = 0
    in_riichi = None
    # array of Tile objects
    discards = None
    # array of tiles in 34 tile format
    safe_tiles = None
    # tiles that were discarded in the current "step"
    # so, for example kamicha discard will be a safe tile for all players
    temporary_safe_tiles = None

    def __init__(self, seat):
        self.seat = seat
        self.is_dealer = False
        self.in_riichi = False
        self.discards = []
        self.temporary_safe_tiles = []
        self.safe_tiles = []

    @property
    def all_safe_tiles(self):
        return self.temporary_safe_tiles + self.safe_tiles


class Defence(object):
    table = None
    players = None

    def __init__(self, table):
        self.table = table
        # 0 is our bot, so we don't need to analyze this player
        # 1, 2, 3 is our enemies
        self.players = {
            1: PlayerMeta(1),
            2: PlayerMeta(2),
            3: PlayerMeta(3)
        }

    def add_discarded_tile(self, player_seat, tile: Tile):
        """
        :param player_seat: 1, 2 or 3
        :param tile:
        """
        self.players[player_seat].discards.append(tile)
        self.add_safe_tile(player_seat, tile.value)

    def add_safe_tile(self, player_seat, tile):
        """
        Player's discard or tiles that were discarded after player riichi
        :param player_seat: 1, 2 or 3
        :param tile: 136 tile format
        :return:
        """
        tile //= 4
        player = self.players[player_seat]
        if tile not in player.safe_tiles:
            player.safe_tiles.append(tile)

        # all tiles that were discarded after player riichi will be safe against him
        # because of furiten
        for player in self.players.values():
            if player.in_riichi and tile not in player.safe_tiles:
                player.safe_tiles.append(tile)

        # erase temporary furiten after tile draw
        self.players[player_seat].temporary_safe_tiles = []
        affected_players = [1, 2, 3]
        affected_players.remove(player_seat)
        # temporary furiten, for one "step"
        for x in affected_players:
            if tile not in self.players[x].temporary_safe_tiles:
                self.players[x].temporary_safe_tiles.append(tile)

    def called_riichi(self, player_seat):
        """
        :param player_seat: 1, 2 or 3
        """
        self.players[player_seat].in_riichi = True

    def set_dealer(self, player_seat):
        """
        :param player_seat: 1, 2 or 3
        """
        self.players[player_seat].is_dealer = True

    def should_go_to_defence_mode(self):
        """
        The method is decides should bot go to the defence mode or not.
        For now only full defence is possible
        :return: true|false
        """
        main_player = self.table.get_main_player()
        current_shanten = main_player.ai.previous_shanten

        # if we are in riichi, we can't defence
        if main_player.in_riichi:
            return False

        count_of_riichi_players = 0
        for player in self.players.values():
            if player.in_riichi:
                count_of_riichi_players += 1

        # no one in riichi, we can build our hand
        if count_of_riichi_players == 0:
            return False

        # our hand is far away from tempai, so better to fold
        if current_shanten >= 1:
            return True

        # we are in tempai, let's try to estimate hand value
        hands_estimated_cost = []
        waiting = main_player.ai.waiting
        for tile in waiting:
            hand_result = main_player.ai.estimate_hand_value(tile)
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

    def try_to_find_safe_tile_to_discard(self):
        closed_hand = self.table.get_main_player().closed_hand
        closed_hand_34 = TilesConverter.to_34_array(closed_hand)
        threatening_players = self._get_threatening_players()

        safe_tiles = [x.all_safe_tiles for x in threatening_players]
        common_safe_tiles = list(set.intersection(*map(set, safe_tiles)))
        # we found a tile that is safe and common for all riichi players
        if common_safe_tiles:
            for safe_tile in common_safe_tiles:
                for i in range(0, len(closed_hand_34)):
                    if closed_hand_34[i] > 0 and i == safe_tile:
                        return TilesConverter.find_34_tile_in_136_array(safe_tile, closed_hand)

        most_threatening_player = self._get_most_threatening_player(threatening_players)
        safe_tiles = most_threatening_player.all_safe_tiles

        for safe_tile in safe_tiles:
            for i in range(0, len(closed_hand_34)):
                if closed_hand_34[i] > 0 and i == safe_tile:
                    return TilesConverter.find_34_tile_in_136_array(safe_tile, closed_hand)

        # we wasn't able to find gembutsu
        return None

    def _get_threatening_players(self) -> [PlayerMeta]:
        """
        For now it is just players in riichi,
        later I will add players with opened valuable hands
        :return: [PlayerMeta]
        """
        result = []
        for player in self.players.values():
            if player.in_riichi:
                result.append(player)
        return result

    def _get_most_threatening_player(self, threatening_players) -> PlayerMeta:
        """
        For now it will be just a dealer.
        Later I will add discard analyze
        :param threatening_players
        :return: PlayerMeta
        """
        for player in threatening_players:
            if player.seat == self.table.dealer_seat:
                return player

        # dealer is not in threatening players list
        return threatening_players[0]

