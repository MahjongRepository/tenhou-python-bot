# -*- coding: utf-8 -*-

# d e f g t u v w
GAME_TYPE = 'z'
MELD_TAG = 'm'
RIICHI_TAG = 'r'
DORA_TAG = 'a'
INIT_TAG = 'i'
AGARI_TAG = 'o'

DELIMITER = ';'
TAGS_DELIMITER = '\n'


class BaseTag(object):
    tag_name = ''

    def _values(self):
        raise NotImplemented()

    def __str__(self):
        return '{}'.format(DELIMITER).join([str(x) for x in self._values()])


class DiscardAndDrawTag(BaseTag):
    discard = 0

    # d e f g t u v w tag names
    def __init__(self, tag_name, discard):
        self.tag_name = tag_name
        self.discard = discard

    def _values(self):
        return [self.tag_name, self.discard]


class GameTypeTag(BaseTag):
    tag_name = GAME_TYPE

    game_type = 0

    def __init__(self, game_type):
        self.game_type = game_type

    def _values(self):
        return [self.tag_name, self.game_type]


class MeldTag(BaseTag):
    tag_name = MELD_TAG

    meld_string = ''
    who = 0

    def __init__(self, who, meld):
        self.who = who
        self.meld_string = meld

    def _values(self):
        return [self.tag_name, self.who, self.meld_string]


class RiichiTag(BaseTag):
    tag_name = RIICHI_TAG

    who = 0
    step = 0

    def __init__(self, who, step):
        self.who = who
        self.step = step

    def _values(self):
        return [self.tag_name, self.who, self.step]


class DoraTag(BaseTag):
    tag_name = DORA_TAG

    tile = 0

    def __init__(self, tile):
        self.tile = tile

    def _values(self):
        return [self.tag_name, self.tile]


class InitTag(BaseTag):
    tag_name = INIT_TAG

    first_hand = ''
    second_hand = ''
    third_hand = ''
    fourth_hand = ''
    dealer = ''
    count_of_honba_sticks = ''
    count_of_riichi_sticks = ''
    dora_indicator = ''

    def __init__(self, first_hand, second_hand, third_hand, fourth_hand, dealer, count_of_honba_sticks,
                 count_of_riichi_sticks, dora_indicator):
        self.first_hand = first_hand
        self.second_hand = second_hand
        self.third_hand = third_hand
        self.fourth_hand = fourth_hand
        self.dealer = dealer
        self.count_of_honba_sticks = count_of_honba_sticks
        self.count_of_riichi_sticks = count_of_riichi_sticks
        self.dora_indicator = dora_indicator

    def _values(self):
        return [self.tag_name, self.first_hand, self.second_hand, self.third_hand,
                self.fourth_hand, self.dealer, self.count_of_honba_sticks, self.count_of_riichi_sticks,
                self.dora_indicator]


class AgariTag(BaseTag):
    tag_name = AGARI_TAG

    who = 0
    from_who = 0
    ura_dora = ''
    closed_hand = ''
    open_melds = ''
    win_tile = ''
    win_scores = ''
    yaku_list = ''
    fu = ''

    def __init__(self, who, from_who, ura_dora, closed_hand, open_melds, win_scores, win_tile, yaku_list, fu):
        self.who = who
        self.from_who = from_who
        self.ura_dora = ura_dora
        self.closed_hand = closed_hand
        self.open_melds = open_melds
        self.win_scores = win_scores
        self.win_tile = win_tile
        self.yaku_list = yaku_list
        self.fu = fu

    def _values(self):
        return [self.tag_name, self.who, self.from_who, self.ura_dora, self.closed_hand,
                self.open_melds, self.win_scores, self.win_tile, self.yaku_list, self.fu]
