# -*- coding: utf-8 -*-
import os

import re
from bs4 import BeautifulSoup

# need to find out better way to do relative imports
# noinspection PyUnresolvedReferences
from tags import GameTypeTag, DiscardAndDrawTag, AgariTag, DoraTag, MeldTag, InitTag, RiichiTag, TAGS_DELIMITER

data_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


class TenhouLogCompressor(object):
    log_name = ''
    tags = []

    def compress(self, log_name):
        content = self._get_log_content(log_name)

        soup = BeautifulSoup(content, 'html.parser')
        elements = soup.find_all()

        skip_tags = ['mjloggm', 'shuffle', 'un', 'taikyoku', 'bye', 'ryuukyoku']
        for tag in elements:
            if tag.name in skip_tags:
                continue

            match_discard = re.match(r"^[defgtuvw]+\d.*", tag.name)
            if match_discard:
                self.tags.append(self.parse_draw_and_discard(tag))

            if tag.name == 'go':
                self.tags.append(self.parse_game_type(tag))

            if tag.name == 'n':
                self.tags.append(self.parse_meld(tag))

            if tag.name == 'reach':
                self.tags.append(self.parse_riichi(tag))

            if tag.name == 'dora':
                self.tags.append(self.parse_dora(tag))

            if tag.name == 'init':
                self.tags.append(self.parse_init_round(tag))

            if tag.name == 'agari':
                self.tags.append(self.parse_agari_round(tag))

        return self._save_results()

    def parse_draw_and_discard(self, tag):
        tile = re.findall(r'\d+', tag.name)[0]
        tag_name = re.findall(r'^[defgtuvw]+', tag.name)[0]
        return DiscardAndDrawTag(tag_name, tile)

    def parse_game_type(self, tag):
        return GameTypeTag(tag.attrs['type'])

    def parse_meld(self, tag):
        return MeldTag(tag.attrs['who'], tag.attrs['m'])

    def parse_riichi(self, tag):
        return RiichiTag(tag.attrs['who'], tag.attrs['step'])

    def parse_dora(self, tag):
        return DoraTag(tag.attrs['hai'])

    def parse_init_round(self, tag):
        seed = tag.attrs['seed'].split(',')
        count_of_honba_sticks = seed[1]
        count_of_riichi_sticks = seed[2]
        dora_indicator = seed[5]

        return InitTag(
            tag.attrs['hai0'],
            tag.attrs['hai1'],
            tag.attrs['hai2'],
            tag.attrs['hai3'],
            tag.attrs['oya'],
            count_of_honba_sticks,
            count_of_riichi_sticks,
            dora_indicator,
        )

    def parse_agari_round(self, tag):
        temp = tag.attrs['ten'].split(',')
        fu = temp[0]
        win_scores = temp[1]

        yaku_list = ''
        if 'yaku' in tag.attrs:
            yaku_list = tag.attrs['yaku']

        if 'yakuman' in tag.attrs:
            yakuman_list = tag.attrs['yakuman'].split(',')
            yaku_list = ','.join(['{},13'.format(x) for x in yakuman_list])

        ura_dora = 'dorahaiura' in tag.attrs and tag.attrs['dorahaiura'] or ''
        melds = 'm' in tag.attrs and tag.attrs['m'] or ''

        return AgariTag(
            tag.attrs['who'],
            tag.attrs['fromwho'],
            ura_dora,
            tag.attrs['hai'],
            melds,
            win_scores,
            tag.attrs['machi'],
            yaku_list,
            fu
        )

    def _save_results(self):
        log_name = os.path.join(data_directory, 'results', self.log_name.split('/')[-1])
        with open(log_name, 'w') as f:
            f.write('{}'.format(TAGS_DELIMITER).join([str(tag) for tag in self.tags]))
        return True

    def _get_log_content(self, log_name):
        self.log_name = log_name

        log_name = os.path.join(data_directory, log_name)
        with open(log_name, 'r') as f:
            return f.read()


class TenhouLogCompressorNoFile(TenhouLogCompressor):
    content = ''

    def __init__(self, content):
        self.content = content
        self.tags = []

    def _get_log_content(self, log_name):
        return self.content

    def _save_results(self):
        return '{}'.format(TAGS_DELIMITER).join([str(tag) for tag in self.tags])
