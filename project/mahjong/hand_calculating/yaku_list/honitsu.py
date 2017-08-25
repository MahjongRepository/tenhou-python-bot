# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Honitsu(Yaku):

    def set_attributes(self):
        self.yaku_id = 34
        self.name = 'Honitsu'

        self.han_open = 2
        self.han_closed = 3

        self.is_yakuman = False

    def is_condition_met(self, hand):
        return True
