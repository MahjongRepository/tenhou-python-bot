class YakuAnalyzer:
    def get_safe_tiles_34(self):
        return []

    def get_bonus_danger(self, tile_136, number_of_revealed_tiles):
        return []

    def get_tempai_probability_modifier(self):
        return 1

    def is_absorbed(self, possible_yaku, tile_34=None):
        return False

    def _is_absorbed_by(self, possible_yaku, id, tile_34):
        absorbing_yaku_possible = [x for x in possible_yaku if x.id == id]
        if absorbing_yaku_possible:
            analyzer = absorbing_yaku_possible[0]
            if tile_34 is None:
                return True

            if not (tile_34 in analyzer.get_safe_tiles_34()):
                return True

        return False
