from mahjong.tile import TilesConverter


class Defence(object):
    table = None

    def __init__(self, table):
        self.table = table

    def go_to_defence_mode(self):
        """
        The method is decides should main player go to the defence mode or not
        :return: true|false
        """
        main_player = self.table.get_main_player()
        result = False

        # if we are in riichi, we can't defence
        if main_player.in_riichi:
            return False

        for player in self.table.players:
            if player.seat == main_player.seat:
                continue

            if player.in_riichi:
                result = True

        return result

    def calculate_safe_tile_against_riichi(self):
        player_tiles = self.table.get_main_player().tiles
        # tiles that were discarded after riichi or
        # discarded by player in riichi
        # for better experience we need to detect the safe tiles for different players
        safe_tiles = []
        for player in self.table.players:
            safe_tiles += player.safe_tiles
            if player.in_riichi:
                safe_tiles += player.discards

        player_tiles_34 = TilesConverter.to_34_array(player_tiles)
        safe_tiles_34 = TilesConverter.to_34_array(safe_tiles)

        safe_tile = None
        # let's try to find a safe tile in our main player hand
        for i in range(0, len(safe_tiles_34)):
            if safe_tiles_34[i] > 0 and player_tiles_34[i] > 0:
                return TilesConverter.find_34_tile_in_136_array(i, player_tiles)

        return safe_tile
