from game.ai.defence.yaku_analyzer.yaku_analyzer import YakuAnalyzer
from mahjong.utils import is_honor


class HonitsuAnalyzerBase(YakuAnalyzer):
    chosen_suit = None

    def __init__(self, enemy):
        self.enemy = enemy
        self.chosen_suit = None

    def serialize(self):
        return {"id": self.id, "chosen_suit": self.chosen_suit and self.chosen_suit.__name__}

    def get_tempai_probability_modifier(self):
        # if enemy has not yet discarded his suit and there are less than 3 melds, consider tempai less probable
        suit_discards = [x for x in self.enemy.discards if self.chosen_suit(x.value // 4)]

        if not suit_discards and len(self.enemy.melds) <= 3:
            return 0.5

        return 1

    def _check_discard_order(self, suit, early_position):
        # let's check the following considiton:
        # if enemy had discarded tiles from that suit or honor and after that he had discarded a tile from a different
        # suit from his hand - let's believe it's not honitsu
        suit_discards_positions = [
            self.enemy.discards.index(x) for x in self.enemy.discards if suit["function"](x.value // 4)
        ]
        if suit_discards_positions:
            # we consider second discard of chosen suit to be reference point
            # first one could have happened when player was not yet sure if he is going to honitsu
            # after the second one there should be no discars of other suit from hand
            reference_discard = suit_discards_positions[min(1, len(suit_discards_positions) - 1)]
            discards_after = self.enemy.discards[reference_discard:]
            if discards_after:
                has_discarded_other_suit_from_hand = [
                    x
                    for x in discards_after
                    if (not x.is_tsumogiri and not is_honor(x.value // 4) and not suit["function"](x.value // 4))
                ]
                if has_discarded_other_suit_from_hand:
                    return False

            # if we started discards suit tiles early, it's probably not honitsu
            if suit_discards_positions[0] <= early_position:
                return False

        # discard order seems similar to honitsu/chinitsu one
        return True
