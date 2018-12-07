class YakuhaiAnalyzer:
    id = 'Yakuhai'

    def __init__(self, player):
        self.player = player

    def is_yaku_active(self):
        return len(self.get_suitable_melds()) > 0

    def melds_han(self):
        han = 0
        suitable_melds = self.get_suitable_melds()
        for x in suitable_melds:
            tile_34 = x.tiles[0] // 4
            # we need to do that to support double winds yakuhais
            han += len([x for x in self.player.valued_honors if x == tile_34])
        return han

    def get_suitable_melds(self):
        suitable_melds = []
        for x in self.player.melds:
            tile_34 = x.tiles[0] // 4
            if tile_34 in self.player.valued_honors:
                suitable_melds.append(x)
        return suitable_melds

    def get_safe_tiles(self):
        """
        There are no safe tiles against yakuhai
        """
        return []
