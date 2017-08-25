# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class DaiSuushii(Yaku):
    """
    Yaku situation
    """

    def set_attributes(self):
        self.yaku_id = 49
        self.name = 'Dai Suushii'

        self.han_open = 26
        self.han_closed = 26

        self.is_yakuman = True

    def is_condition_met(self, hand):
        # was it here or not is controlling by superior code
        return True
