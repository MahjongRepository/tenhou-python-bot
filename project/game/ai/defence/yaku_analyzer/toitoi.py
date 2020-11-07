from copy import copy

from game.ai.defence.yaku_analyzer.yaku_analyzer import YakuAnalyzer
from game.ai.helpers.defence import TileDanger
from mahjong.utils import plus_dora
from utils.decisions_logger import MeldPrint


class ToitoiAnalyzer(YakuAnalyzer):
    id = "toitoi"

    def __init__(self, enemy):
        self.enemy = enemy

    def serialize(self):
        return {"id": self.id}

    def is_yaku_active(self):
        if len(self.enemy.melds) < 2:
            return False

        for meld in self.enemy.melds:
            if meld.type == MeldPrint.CHI:
                return False

        if len(self.enemy.discards) < 10:
            return len(self.enemy.melds) >= 3

        return True

    def melds_han(self):
        return 2

    def get_safe_tiles_34(self):
        # FIXME: tiles that player cannot wait in tanki/syanpon should be considered safe
        return []

    def get_bonus_danger(self, tile_136, number_of_revealed_tiles):
        bonus_danger = []
        tile_34 = tile_136 // 4
        number_of_yakuhai = self.enemy.valued_honors.count(tile_34)

        # shonpai tiles
        if number_of_revealed_tiles == 1:
            # aka doras don't get additional danger against toitoi, they just get their regular one
            dora_count = plus_dora(tile_136, self.enemy.table.dora_indicators)
            if dora_count > 0:
                danger = copy(TileDanger.TOITOI_SHONPAI_DORA_BONUS_DANGER)
                danger["value"] = dora_count * danger["value"]
                danger["dora_count"] = dora_count
                bonus_danger.append(danger)

            if number_of_yakuhai > 0:
                bonus_danger.append(TileDanger.TOITOI_SHONPAI_YAKUHAI_BONUS_DANGER)
            else:
                bonus_danger.append(TileDanger.TOITOI_SHONPAI_NON_YAKUHAI_BONUS_DANGER)
        elif number_of_revealed_tiles == 2:
            if number_of_yakuhai > 0:
                bonus_danger.append(TileDanger.TOITOI_SECOND_YAKUHAI_HONOR_BONUS_DANGER)
        elif number_of_revealed_tiles == 3:
            # FIXME: we should add negative bonus danger exclusively against toitoi for such tiles
            # except for doras and honors maybe
            pass

        return bonus_danger
