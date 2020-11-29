from game.ai.defence.yaku_analyzer.yaku_analyzer import YakuAnalyzer
from mahjong.constants import HONOR_INDICES, TERMINAL_INDICES


class TanyaoAnalyzer(YakuAnalyzer):
    id = "tanyao"

    def __init__(self, enemy):
        self.enemy = enemy

    def serialize(self):
        return {"id": self.id}

    def is_yaku_active(self):
        return len(self._get_suitable_melds()) > 0

    def melds_han(self):
        return len(self._get_suitable_melds()) > 0 and 1 or 0

    def _get_suitable_melds(self):
        suitable_melds = []
        for meld in self.enemy.melds:
            tiles_34 = [x // 4 for x in meld.tiles]
            not_suitable_tiles = TERMINAL_INDICES + HONOR_INDICES
            if not any(x in not_suitable_tiles for x in tiles_34):
                suitable_melds.append(meld)
            else:
                # if there is an unsuitable meld we consider tanyao impossible
                return []

        return suitable_melds

    def get_safe_tiles_34(self):
        return TERMINAL_INDICES + HONOR_INDICES
