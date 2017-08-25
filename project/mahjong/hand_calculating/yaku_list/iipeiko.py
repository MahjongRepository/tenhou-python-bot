# -*- coding: utf-8 -*-
from mahjong.hand_calculating.yaku import Yaku


class Iipeiko(Yaku):

    def set_attributes(self):
        self.yaku_id = 7
        self.name = 'Iipeiko'

        self.han_open = None
        self.han_closed = 1

        self.is_yakuman = False

    def is_condition_met(self, hand):
        return True
