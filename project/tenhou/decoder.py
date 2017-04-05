# -*- coding: utf-8 -*-
from urllib.parse import unquote

import re
from mahjong.meld import Meld


class TenhouDecoder(object):
    RANKS = [
        u'新人',
        u'9級',
        u'8級',
        u'7級',
        u'6級',
        u'5級',
        u'4級',
        u'3級',
        u'2級',
        u'1級',
        u'初段',
        u'二段',
        u'三段',
        u'四段',
        u'五段',
        u'六段',
        u'七段',
        u'八段',
        u'九段',
        u'十段',
        u'天鳳位'
    ]

    def parse_hello_string(self, message):
        rating_string = ''
        if 'auth=' in message:
            auth_message = self.get_attribute_content(message, 'auth')
            # for NoName we don't have rating attribute
            if 'PF4=' in message:
                rating_string = self.get_attribute_content(message, 'PF4')
            return auth_message, rating_string
        else:
            return '', ''

    def parse_initial_values(self, message):
        """
        Six element list:
            - Round number,
            - Number of honba sticks,
            - Number of riichi sticks,
            - First dice minus one,
            - Second dice minus one,
            - Dora indicator.
        """

        seed = self.get_attribute_content(message, 'seed').split(',')
        seed = [int(i) for i in seed]

        round_number = seed[0]
        count_of_honba_sticks = seed[1]
        count_of_riichi_sticks = seed[2]
        dora_indicator = seed[5]
        dealer = int(self.get_attribute_content(message, 'oya'))

        scores = self.get_attribute_content(message, 'ten').split(',')
        scores = [int(i) for i in scores]

        return {
            'round_number': round_number,
            'count_of_honba_sticks': count_of_honba_sticks,
            'count_of_riichi_sticks': count_of_riichi_sticks,
            'dora_indicator': dora_indicator,
            'dealer': dealer,
            'scores': scores
        }

    def parse_initial_hand(self, message):
        tiles = self.get_attribute_content(message, 'hai')
        tiles = [int(i) for i in tiles.split(',')]
        return tiles

    def parse_final_scores_and_uma(self, message):
        data = self.get_attribute_content(message, 'owari')
        data = [float(i) for i in data.split(',')]

        # start at the beginning at take every second item (even)
        scores = data[::2]
        # start at second item and take every second item (odd)
        uma = data[1::2]

        return {'scores': scores, 'uma': uma}

    def parse_names_and_ranks(self, message):
        ranks = self.get_attribute_content(message, 'dan')
        ranks = [int(i) for i in ranks.split(',')]

        return [
            {'name': unquote(self.get_attribute_content(message, 'n0')), 'rank': TenhouDecoder.RANKS[ranks[0]]},
            {'name': unquote(self.get_attribute_content(message, 'n1')), 'rank': TenhouDecoder.RANKS[ranks[1]]},
            {'name': unquote(self.get_attribute_content(message, 'n2')), 'rank': TenhouDecoder.RANKS[ranks[2]]},
            {'name': unquote(self.get_attribute_content(message, 'n3')), 'rank': TenhouDecoder.RANKS[ranks[3]]},
        ]

    def parse_log_link(self, message):
        seat = int(self.get_attribute_content(message, 'oya'))
        seat = (4 - seat) % 4
        game_id = self.get_attribute_content(message, 'log')
        return game_id, seat

    def parse_tile(self, message):
        # tenhou format: <t23/>, <e23/>, <f23 t="4"/>, <f23/>, <g23/>
        result = re.match(r'^<[tefgEFGTUVWD]+\d*', message).group()
        return int(result[2:])

    def parse_table_state_after_reconnection(self, message):
        players = []
        for x in range(0, 4):
            player = {
                'discards': [],
                'melds': []
            }

            discard_attr = 'kawa{}'.format(x)
            if discard_attr in message:
                discards = self.get_attribute_content(message, discard_attr)
                discards = [int(x) for x in discards.split(',')]

                was_riichi = 255 in discards
                if was_riichi:
                    discards.remove(255)

                player['discards'] = discards

            melds_attr = 'm{}'.format(x)
            if melds_attr in message:
                melds = self.get_attribute_content(message, melds_attr)
                melds = [int(x) for x in melds.split(',')]
                for item in melds:
                    meld_message = '<N who="{}" m="{}" />'.format(x, item)
                    meld = self.parse_meld(meld_message)
                    player['melds'].append(meld)

            players.append(player)

        for player in players:
            for meld in player['melds']:
                players[meld.from_who]['discards'].append(meld.called_tile)

        return players

    def parse_dora_indicator(self, message):
        return int(self.get_attribute_content(message, 'hai'))

    def parse_who_called_riichi(self, message):
        return int(self.get_attribute_content(message, 'who'))

    def parse_go_tag(self, message):
        return int(self.get_attribute_content(message, 'type'))

    def parse_meld(self, message):
        data = int(self.get_attribute_content(message, 'm'))

        meld = Meld()
        meld.who = int(self.get_attribute_content(message, 'who'))
        meld.from_who = data & 0x3

        if data & 0x4:
            self.parse_chi(data, meld)
        elif data & 0x18:
            self.parse_pon(data, meld)
        elif data & 0x20:
            self.parse_nuki(data, meld)
        else:
            self.parse_kan(data, meld)

        return meld

    def parse_chi(self, data, meld):
        meld.type = Meld.CHI
        t0, t1, t2 = (data >> 3) & 0x3, (data >> 5) & 0x3, (data >> 7) & 0x3
        base_and_called = data >> 10
        base = base_and_called // 3
        called = base_and_called % 3
        base = (base // 7) * 9 + base % 7
        meld.tiles = [t0 + 4 * (base + 0), t1 + 4 * (base + 1), t2 + 4 * (base + 2)]
        meld.called_tile = meld.tiles[called]

    def parse_pon(self, data, meld):
        t4 = (data >> 5) & 0x3
        t0, t1, t2 = ((1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2))[t4]
        base_and_called = data >> 9
        base = base_and_called // 3
        called = base_and_called % 3
        if data & 0x8:
            meld.type = Meld.PON
            meld.tiles = [t0 + 4 * base, t1 + 4 * base, t2 + 4 * base]
        else:
            meld.type = Meld.CHAKAN
            meld.tiles = [t0 + 4 * base, t1 + 4 * base, t2 + 4 * base, t4 + 4 * base]
        meld.called_tile = meld.tiles[called]

    def parse_kan(self, data, meld):
        base_and_called = data >> 8
        base = base_and_called // 4
        meld.type = Meld.KAN
        meld.tiles = [4 * base, 1 + 4 * base, 2 + 4 * base, 3 + 4 * base]
        if meld.from_who:
            called = base_and_called % 4
            meld.called_tile = meld.tiles[called]

    def parse_nuki(self, data, meld):
        meld.type = Meld.NUKI
        meld.tiles = [data >> 8]

    def generate_auth_token(self, auth_string):
        translation_table = [63006, 9570, 49216, 45888, 9822, 23121, 59830, 51114, 54831, 4189, 580, 5203, 42174, 59972,
                             55457, 59009, 59347, 64456, 8673, 52710, 49975, 2006, 62677, 3463, 17754, 5357]

        parts = auth_string.split('-')
        if len(parts) != 2:
            return False

        first_part = parts[0]
        second_part = parts[1]
        if len(first_part) != 8 and len(second_part) != 8:
            return False

        table_index = int('2' + first_part[2:8]) % (12 - int(first_part[7:8])) * 2

        a = translation_table[table_index] ^ int(second_part[0:4], 16)
        b = translation_table[table_index + 1] ^ int(second_part[4:8], 16)

        postfix = format(a, '2x') + format(b, '2x')

        result = first_part + '-' + postfix

        return result

    def get_attribute_content(self, message, attribute_name):
        result = re.findall(r'{}="([^"]*)"'.format(attribute_name), message)
        return result and result[0] or None
