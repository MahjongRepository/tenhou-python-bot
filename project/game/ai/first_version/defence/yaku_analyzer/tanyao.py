from mahjong.constants import HONOR_INDICES, TERMINAL_INDICES


class TanyaoAnalyzer:
    id = "Tanyao"

    def __init__(self, player):
        self.player = player

    def is_yaku_active(self):
        return len(self.get_suitable_melds()) > 0

    def melds_han(self):
        return len(self.get_suitable_melds()) > 0 and 1 or 0

    def get_suitable_melds(self):
        suitable_melds = []
        for meld in self.player.melds:
            tiles_34 = [x // 4 for x in meld.tiles]
            not_suitable_tiles = TERMINAL_INDICES + HONOR_INDICES
            if not any(x in not_suitable_tiles for x in tiles_34):
                suitable_melds.append(meld)
        return suitable_melds

    def get_dangerous_tiles(self):
        all_tiles_34 = range(0, 34)
        return list(set(all_tiles_34) - set(TERMINAL_INDICES) - set(HONOR_INDICES))
