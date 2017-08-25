# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Suukantsu(Yaku):

    def set_attributes(self):
        self.yaku_id = 51
        self.name = 'Suu kantsu'

        self.han_open = 13
        self.han_closed = 13

        self.is_yakuman = True

    def is_condition_met(self, hand):
        return True
