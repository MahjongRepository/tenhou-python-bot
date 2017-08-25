# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Chinitsu(Yaku):

    def set_attributes(self):
        self.yaku_id = 35
        self.name = 'Chinitsu'

        self.han_open = 5
        self.han_closed = 6

        self.is_yakuman = False

    def is_condition_met(self, hand):
        return True
