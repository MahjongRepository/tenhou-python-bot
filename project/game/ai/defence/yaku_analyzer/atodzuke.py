from game.ai.defence.yaku_analyzer.yaku_analyzer import YakuAnalyzer
from game.ai.helpers.defence import TileDanger
from mahjong.utils import is_honor


class AtodzukeAnalyzer(YakuAnalyzer):
    id = "atodzuke_yakuhai"

    def __init__(self, enemy):
        self.enemy = enemy

    def serialize(self):
        return {"id": self.id}

    # we must check atodzuke after all other yaku and only if there are no other yaku
    # so activation check is on the caller's side
    def is_yaku_active(self):
        return True

    def melds_han(self):
        return 1

    def get_safe_tiles_34(self):
        safe_tiles = []
        for x in range(0, 34):
            if not is_honor(x):
                safe_tiles.append(x)
            elif not self.enemy.valued_honors.count(x):
                safe_tiles.append(x)

        return safe_tiles

    def get_bonus_danger(self, tile_136, number_of_revealed_tiles):
        bonus_danger = []
        tile_34 = tile_136 // 4
        number_of_yakuhai = self.enemy.valued_honors.count(tile_34)

        if number_of_yakuhai > 0 and number_of_revealed_tiles < 3:
            bonus_danger.append(TileDanger.ATODZUKE_YAKUHAI_HONOR_BONUS_DANGER)

        return bonus_danger

    def is_absorbed(self, possible_yaku, tile_34=None):
        return len(possible_yaku) > 1
