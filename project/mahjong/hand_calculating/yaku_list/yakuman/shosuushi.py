# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Shousuushii(Yaku):
    """
    Yaku situation
    """

    def set_attributes(self):
        self.yaku_id = 50
        self.name = 'Shousuushii'

        self.han_open = 13
        self.han_closed = 13

        self.is_yakuman = True

    def is_condition_met(self, hand, *args):
        # was it here or not is controlling by superior code
        return True
