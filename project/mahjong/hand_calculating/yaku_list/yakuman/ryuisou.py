# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Ryuuiisou(Yaku):
    """
    Yaku situation
    """

    def set_attributes(self):
        self.yaku_id = 43
        self.name = 'Ryuuiisou'

        self.han_open = 13
        self.han_closed = 13

        self.is_yakuman = True

    def is_condition_met(self, hand):
        # was it here or not is controlling by superior code
        return True
