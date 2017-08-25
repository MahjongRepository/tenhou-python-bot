# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Chanta(Yaku):

    def set_attributes(self):
        self.yaku_id = 23
        self.name = 'Chanta'

        self.han_open = 1
        self.han_closed = 2

        self.is_yakuman = False

    def is_condition_met(self, hand):
        return True
