# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Toitoi(Yaku):

    def set_attributes(self):
        self.yaku_id = 31
        self.name = 'Toitoi'

        self.han_open = 2
        self.han_closed = 2

        self.is_yakuman = False

    def is_condition_met(self, hand):
        return True
