import re

from mahjong.ai.discard import DiscardOption
from mahjong.table import Table
from mahjong.tile import TilesConverter
from tenhou.decoder import TenhouDecoder


class Reproducer(object):
    round_content = None
    player_position = None
    stop_tag = None

    def __init__(self, round_content, player_position, stop_tag):
        """
        :param round_content: array of round tags
        :param player_position: position of the player that will be our bot
        """
        self.round_content = round_content
        self.player_position = player_position
        self.stop_tag = stop_tag
        self.decoder = TenhouDecoder()

    def reproduce(self, display_tags=False):
        draw_tags = ['T', 'U', 'V', 'W']
        discard_tags = ['D', 'E', 'F', 'G']

        player_draw = draw_tags[self.player_position]

        player_draw_regex = re.compile('^<[{}]+\d*'.format(''.join(player_draw)))
        discard_regex = re.compile('^<[{}]+\d*'.format(''.join(discard_tags)))

        table = Table()
        for tag in self.round_content:
            if display_tags:
                print(tag)

            if not display_tags and tag == self.stop_tag:
                break

            if 'INIT' in tag:
                values = self.decoder.parse_initial_values(tag)

                shifted_scores = []
                for x in range(0, 4):
                    shifted_scores.append(values['scores'][self.normalize_position(x, self.player_position)])

                table.init_round(
                    values['round_number'],
                    values['count_of_honba_sticks'],
                    values['count_of_riichi_sticks'],
                    values['dora_indicator'],
                    self.normalize_position(self.player_position, values['dealer']),
                    shifted_scores,
                )

                hands = [
                    [int(x) for x in self.decoder.get_attribute_content(tag, 'hai0').split(',')],
                    [int(x) for x in self.decoder.get_attribute_content(tag, 'hai1').split(',')],
                    [int(x) for x in self.decoder.get_attribute_content(tag, 'hai2').split(',')],
                    [int(x) for x in self.decoder.get_attribute_content(tag, 'hai3').split(',')],
                ]

                table.player.init_hand(hands[self.player_position])

            if player_draw_regex.match(tag) and 'UN' not in tag:
                tile = self.decoder.parse_tile(tag)
                table.player.draw_tile(tile)

            if discard_regex.match(tag) and 'DORA' not in tag:
                tile = self.decoder.parse_tile(tag)
                player_sign = tag.upper()[1]
                player_seat = self.normalize_position(self.player_position, discard_tags.index(player_sign))

                if player_seat == 0:
                    table.player.discard_tile(DiscardOption(table.player, tile // 4, 0, [], 0))
                else:
                    table.add_discarded_tile(player_seat, tile, False)

            if '<N who=' in tag:
                meld = self.decoder.parse_meld(tag)
                player_seat = self.normalize_position(self.player_position, meld.who)
                table.add_called_meld(player_seat,  meld)

                if player_seat == 0:
                    table.player.draw_tile(meld.called_tile)

            if '<REACH' in tag and 'step="1"' in tag:
                who_called_riichi = self.normalize_position(self.player_position,
                                                            self.decoder.parse_who_called_riichi(tag))
                table.add_called_riichi(who_called_riichi)

        if not display_tags:
            tile = self.decoder.parse_tile(self.stop_tag)
            print('Hand: {}'.format(table.player.format_hand_for_print(tile)))

            # to rebuild all caches
            table.player.draw_tile(tile)
            tile = table.player.discard_tile()

            table.player.draw_tile(tile)
            tile = table.player.discard_tile()

            print('Discard: {}'.format(TilesConverter.to_one_line_string([tile])))

    def normalize_position(self, who, from_who):
        positions = [0, 1, 2, 3]
        return positions[who - from_who]
