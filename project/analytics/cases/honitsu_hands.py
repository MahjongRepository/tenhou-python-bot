# -*- coding: utf-8 -*-
import os
import re

import logging

import sqlite3
from distutils.dir_util import mkpath

from analytics.cases.main import ProcessDataCase
from mahjong.ai.shanten import Shanten
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_man, is_pin, is_sou, is_honor

logger = logging.getLogger('process')


class HonitsuHands(ProcessDataCase):
    HONITSU_ID = 34
    CHINITSU_ID = 35

    YAKU_NAMES = {
        HONITSU_ID: 'honitsu',
        CHINITSU_ID: 'chinitsu',
    }

    SUIT_NAMES = [
        'man',
        'pin',
        'sou'
    ]

    # order is important
    suits = [
        is_man,
        is_pin,
        is_sou
    ]

    def __init__(self, db_file):
        super().__init__(db_file)

        db_directory = os.path.join(self.current_directory, '..', 'temp')
        self.local_db_file = os.path.join(db_directory, 'honitsu.db')
        if not os.path.exists(db_directory):
            mkpath(db_directory)

    def process(self):
        self.prepare_data()
        # self.analyze_prepared_data()
        logger.info('Done')

    def prepare_data(self):
        self._set_up_database()

        self.load_all_records()

        filtered_rounds = self.filter_rounds()
        filtered_rounds = self._collect_round_data(filtered_rounds)
        self._save_data(filtered_rounds)

    def analyze_prepared_data(self):
        results = self._load_data()

        for result in results[:10]:
            self._debug_honitsu_data(result)

    def filter_rounds(self):
        """
        Find all rounds that were ended with honitsu or chinitsu hands
        """
        logger.info('Filtering rounds...')

        filtered_rounds = []

        for game in self.games:
            for round_number in range(0, len(game.rounds)):
                round_content = game.rounds[round_number]
                for tag in round_content:
                    if 'AGARI' in tag and 'yaku=' in tag:
                        yaku_temp = self.decoder.get_attribute_content(tag, 'yaku').split(',')
                        # start at the beginning at take every second item (even)
                        yaku_list = [int(x) for x in yaku_temp[::2]]

                        if self.HONITSU_ID in yaku_list or self.CHINITSU_ID in yaku_list:
                            # handle double ron
                            for x in round_content:
                                if 'AGARI' in x and x != tag:
                                    round_content.remove(x)

                            filtered_rounds.append({
                                'log_id': game.log_id,
                                'year': game.year,
                                'is_tonpusen': game.is_tonpusen,
                                'round_content': round_content,
                                'round_number': round_number,
                            })

        logger.info('Found {} filtered rounds'.format(len(filtered_rounds)))

        return filtered_rounds

    def _collect_round_data(self, filtered_rounds):
        logger.info('Collecting rounds data...')
        draw_tags = ['T', 'U', 'V', 'W']
        discard_tags = ['D', 'E', 'F', 'G']

        shanten = Shanten()

        for round_item in filtered_rounds:
            content = round_item['round_content']
            # it is important to find winner before data processing
            # to collect all data related to this player
            winner = None
            for tag in content:
                if 'AGARI' in tag:
                    winner = int(self.decoder.get_attribute_content(tag, 'who'))
                    break

            revealed_tiles = 0
            open_hand_shanten = None
            open_hand_step = None
            tempai_step = None
            player_hand = []
            winner_draw_regex = re.compile('^<[{}]+\d*'.format(draw_tags[winner]))
            winner_discard_regex = re.compile('^<[{}]+\d*'.format(discard_tags[winner]))
            draw_regex = re.compile(r'^<[TUVW]+\d*')
            for tag in content:
                if 'INIT' in tag:
                    player_hand = self._parse_initial_hand(tag, winner)

                # we need to count revealed tiles
                # to be able associate action with game "step"
                if draw_regex.match(tag) and 'UN' not in tag:
                    revealed_tiles += 1

                if winner_draw_regex.match(tag) and 'UN' not in tag:
                    tile = self.decoder.parse_tile(tag)
                    player_hand.append(tile)

                if winner_discard_regex.match(tag) and 'DORA' not in tag:
                    shanten_number = shanten.calculate_shanten(TilesConverter.to_34_array(player_hand))
                    if shanten_number == 0:
                        tempai_step = revealed_tiles // 4

                    tile = self.decoder.parse_tile(tag)
                    player_hand.remove(tile)

                if '<N who="{}"'.format(winner) in tag:
                    if not open_hand_shanten:
                        open_hand_shanten = shanten.calculate_shanten(TilesConverter.to_34_array(player_hand))
                        open_hand_step = revealed_tiles // 4

                    meld = self.decoder.parse_meld(tag)
                    if meld.called_tile is not None and meld.type != Meld.CHANKAN:
                        player_hand.append(meld.called_tile)

                    # for closed hand we already added this tile in the hand
                    if meld.type == Meld.KAN or meld.type == Meld.CHANKAN:
                        player_hand.remove(meld.tiles[0])

                        shanten_number = shanten.calculate_shanten(TilesConverter.to_34_array(player_hand))
                        if shanten_number == 0:
                            tempai_step = revealed_tiles // 4

                if 'AGARI' in tag:
                    yaku_temp = self.decoder.get_attribute_content(tag, 'yaku').split(',')
                    yaku_list = [int(x) for x in yaku_temp[::2]]

                    yaku = self.HONITSU_ID in yaku_list and self.HONITSU_ID or self.CHINITSU_ID

                    melds = self.decoder.get_attribute_content(tag, 'm')
                    is_open_hand = melds is not None
                    winner = int(self.decoder.get_attribute_content(tag, 'who'))
                    loser = int(self.decoder.get_attribute_content(tag, 'fromWho'))

                    hand_suit, is_honor_or_suit_dora = self._find_hand_suit(tag)

                    scores_temp = self.decoder.get_attribute_content(tag, 'sc').split(',')
                    scores = [int(x) for x in scores_temp[::2]]
                    winner_scores = scores[winner]

                    scores = sorted(scores, reverse=True)
                    winner_position = scores.index(winner_scores) + 1

                    round_item.update({
                        'winner': winner,
                        'yaku': yaku,
                        'suit': hand_suit,
                        'scores': winner_scores,
                        'winner_position': winner_position,
                        'open_hand_shanten': open_hand_shanten,
                        'round_content': '\n'.join(content),
                        'open_hand_step': open_hand_step,
                        'tempai_step': tempai_step,
                        'is_honor_or_suit_dora': is_honor_or_suit_dora and 1 or 0,
                        'is_tsumo': winner == loser and 1 or 0,
                        'is_open_hand': is_open_hand and 1 or 0,
                        'is_tonpusen': round_item['is_tonpusen'] and 1 or 0,
                    })

        return filtered_rounds

    def _find_hand_suit(self, tag):
        hand_tiles = self._parse_win_hand_tiles(tag)
        dora_34 = int(self.decoder.get_attribute_content(tag, 'doraHai').split(',')[0]) // 4

        hand_tiles = sorted(hand_tiles)
        tile_34 = hand_tiles[0] // 4
        hand_suit = None
        dora_is_honor_or_in_same_suit = False
        for y in range(0, len(self.suits)):
            suit = self.suits[y]
            if suit(tile_34):
                hand_suit = y
                dora_is_honor_or_in_same_suit = is_honor(dora_34) or suit(dora_34)
                break
        return hand_suit, dora_is_honor_or_in_same_suit

    def _parse_win_hand_tiles(self, tag):
        melds = self.decoder.get_attribute_content(tag, 'm')
        hand_tiles = [int(x) for x in self.decoder.get_attribute_content(tag, 'hai').split(',')]
        if melds:
            melds = melds.split(',')
            for meld in melds:
                message = '<N who="0" m="{}">'.format(meld)
                meld = self.decoder.parse_meld(message)
                tiles = meld.tiles
                # remove not needed tile from kan
                if len(tiles) == 4:
                    tiles = tiles[1:4]
                hand_tiles.extend(tiles)
        return hand_tiles

    def _parse_initial_hand(self, tag, winner):
        winner_hand_tag = 'hai{}'.format(winner)
        winner_initial_hand = self.decoder.get_attribute_content(tag, winner_hand_tag).split(',')
        return [int(x) for x in winner_initial_hand]

    def _set_up_database(self):
        connection = sqlite3.connect(self.local_db_file)

        logger.info('Set up a honitsu database')
        with connection:
            cursor = connection.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS data(
                        is_honor_or_suit_dora int,
                        is_open_hand int,
                        is_tonpusen int,
                        is_tsumo int,
                        log_id text,
                        open_hand_shanten int,
                        open_hand_step int,
                        round_content text,
                        round_number int,
                        scores int,
                        suit int,
                        tempai_step int,
                        winner int,
                        winner_position int,
                        yaku int,
                        year int);
            """)

    def _save_data(self, filtered_rounds):
        logger.info('Saving rounds data...')

        connection = sqlite3.connect(self.local_db_file)
        with connection:
            cursor = connection.cursor()
            for round_item in filtered_rounds:
                keys = sorted(round_item.keys())
                values = [round_item[x] for x in keys]

                keys_string = ','.join(keys)
                values_string = ','.join(['?'] * len(keys))

                cursor.execute('INSERT INTO data ({}) VALUES ({})'.format(keys_string, values_string), values)

    def _load_data(self):
        logger.info('Loading data...')

        results = []
        connection = sqlite3.connect(self.local_db_file)
        with connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * from data')
            data = cursor.fetchall()

            keys = ['is_honor_or_suit_dora', 'is_open_hand', 'is_tonpusen', 'is_tsumo',
                    'log_id', 'open_hand_shanten', 'open_hand_step',
                    'round_content', 'round_number', 'scores', 'suit',
                    'tempai_step', 'winner', 'winner_position', 'yaku', 'year']

            for result in data:
                dict_result = {}
                for key_index in range(0, len(keys)):
                    key = keys[key_index]
                    dict_result[key] = result[key_index]

                results.append(dict_result)

        return results

    def _debug_honitsu_data(self, result):
        url = 'http://tenhou.net/0/?log={}&tw={}&ts={}'.format(
            result['log_id'],
            result['winner'],
            result['round_number'],
        )
        logger.info(url)
        logger.info('Year: {}'.format(result['year']))

        logger.info('Suit: {}, Yaku: {}, dora in the suit or honor: {}'.format(
            self.SUIT_NAMES[result['suit']],
            self.YAKU_NAMES[result['yaku']],
            result['is_honor_or_suit_dora'] == 1)
        )

        logger.info('Scores: {}, Position: {}'.format(result['scores'] * 100, result['winner_position']))

        if result['is_open_hand']:
            logger.info('Opened with {} shanten, on the {} step'.format(result['open_hand_shanten'],
                                                                        result['open_hand_step']))
        else:
            logger.info('Closed hand')

        logger.info('Achieved tempai on the {} step'.format(result['tempai_step']))

        logger.info(result['is_tsumo'] and 'Tsumo' or 'Ron')
