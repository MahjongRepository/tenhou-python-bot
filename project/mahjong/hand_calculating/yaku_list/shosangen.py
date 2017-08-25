# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Shosangen(Yaku):

    def set_attributes(self):
        self.yaku_id = 30
        self.name = 'Shou Sangen'

        self.han_open = 2
        self.han_closed = 2

        self.is_yakuman = False

    def is_condition_met(self, hand):
        return True
