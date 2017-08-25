# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Ryanpeikou(Yaku):

    def set_attributes(self):
        self.yaku_id = 32
        self.name = 'Ryanpeikou'

        self.han_open = None
        self.han_closed = 3

        self.is_yakuman = False

    def is_condition_met(self, hand):
        return True
