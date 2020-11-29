from game.ai.defence.yaku_analyzer.yaku_analyzer import YakuAnalyzer


class YakuhaiAnalyzer(YakuAnalyzer):
    id = "yakuhai"

    def __init__(self, enemy):
        self.enemy = enemy

    def serialize(self):
        return {"id": self.id}

    def is_yaku_active(self):
        return len(self._get_suitable_melds()) > 0

    def melds_han(self):
        han = 0
        suitable_melds = self._get_suitable_melds()
        for x in suitable_melds:
            tile_34 = x.tiles[0] // 4
            # we need to do that to support double winds yakuhais
            han += len([x for x in self.enemy.valued_honors if x == tile_34])
        return han

    def _get_suitable_melds(self):
        suitable_melds = []
        for x in self.enemy.melds:
            tile_34 = x.tiles[0] // 4
            if tile_34 in self.enemy.valued_honors:
                suitable_melds.append(x)
        return suitable_melds
