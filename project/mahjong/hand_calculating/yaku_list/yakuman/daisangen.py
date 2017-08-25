# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Daisangen(Yaku):
    """
    Yaku situation
    """

    def set_attributes(self):
        self.yaku_id = 39
        self.name = 'Daisangen'

        self.han_open = 13
        self.han_closed = 13

        self.is_yakuman = True

    def is_condition_met(self, hand):
        # was it here or not is controlling by superior code
        return True
