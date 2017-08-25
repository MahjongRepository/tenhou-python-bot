# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Junchan(Yaku):

    def set_attributes(self):
        self.yaku_id = 33
        self.name = 'Junchan'

        self.han_open = 2
        self.han_closed = 3

        self.is_yakuman = False

    def is_condition_met(self, hand):
        return True
