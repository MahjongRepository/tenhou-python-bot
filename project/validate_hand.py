# -*- coding: utf-8 -*-
"""
Load tenhou replay and validate tenhou hand score with our own system score
Input attribute is file name with tenhou.net log content
"""
import logging
import sys

import os
from bs4 import BeautifulSoup
from functools import reduce

from mahjong.constants import EAST, SOUTH, WEST, NORTH
from mahjong.hand import FinishedHand
from mahjong.tile import TilesConverter
from tenhou.decoder import TenhouDecoder
from utils.settings_handler import settings


logger = logging.getLogger('validate_hand')


def load_content(file_name):
    with open(file_name, 'r') as f:
        content = f.read()

    os.remove(file_name)

    return content


def set_up_logging():
    """
    Main logger for usual bot needs
    """
    logger = logging.getLogger('validate_hand')
    logger.setLevel(logging.DEBUG)

    logs_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')

    if not os.path.exists(logs_directory):
        os.mkdir(logs_directory)

    file_name = 'validate_hand.log'
    fh = logging.FileHandler(os.path.join(logs_directory, file_name))
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)


def main():
    if len(sys.argv) < 2:
        return False

    set_up_logging()

    file_name = sys.argv[1]
    content = load_content(file_name)
    TenhouLogParser().parse_log(content, file_name.split('.')[0].replace('temp/', ''))


class TenhouLogParser(object):

    def parse_log(self, log_data, log_id):
        decoder = TenhouDecoder()
        finished_hand = FinishedHand()

        soup = BeautifulSoup(log_data, 'html.parser')
        elements = soup.find_all()

        settings.FIVE_REDS = True

        total_hand = 0
        successful_hand = 0
        played_rounds = 0

        dealer = 0
        round_wind = EAST

        for tag in elements:
            if tag.name == 'go':
                game_rule_temp = int(tag.attrs['type'])

                # let's skip hirosima games
                hirosima = [17, 81, 25, 89]
                if game_rule_temp in hirosima:
                    print('0,0')
                    return

                no_red_five = [11, 7, 3, 163, 167]
                if game_rule_temp in no_red_five:
                    settings.FIVE_REDS = False

            if tag.name == 'taikyoku':
                dealer = int(tag.attrs['oya'])

            if tag.name == 'init':
                dealer = int(tag.attrs['oya'])
                seed = [int(i) for i in tag.attrs['seed'].split(',')]
                round_number = seed[0]

                if round_number < 4:
                    round_wind = EAST
                elif 4 <= round_number < 8:
                    round_wind = SOUTH
                elif 8 <= round_number < 12:
                    round_wind = WEST
                else:
                    round_wind = NORTH

                played_rounds += 1

            if tag.name == 'agari':
                success = True
                winner = int(tag.attrs['who'])
                from_who = int(tag.attrs['fromwho'])

                closed_hand = [int(i) for i in tag.attrs['hai'].split(',')]
                ten = [int(i) for i in tag.attrs['ten'].split(',')]
                dora_indicators = [int(i) for i in tag.attrs['dorahai'].split(',')]
                if 'dorahaiura' in tag.attrs:
                    dora_indicators += [int(i) for i in tag.attrs['dorahaiura'].split(',')]

                yaku_list = []
                yakuman_list = []
                if 'yaku' in tag.attrs:
                    yaku_temp = [int(i) for i in tag.attrs['yaku'].split(',')]
                    yaku_list = yaku_temp[::2]
                    han = sum(yaku_temp[1::2])
                else:
                    yakuman_list = [int(i) for i in tag.attrs['yakuman'].split(',')]
                    han = len(yakuman_list) * 13

                fu = ten[0]
                cost = ten[1]

                melds = []
                called_kan_indices = []
                if 'm' in tag.attrs:
                    for x in tag.attrs['m'].split(','):
                        message = '<N who={} m={}>'.format(tag.attrs['who'], x)
                        meld = decoder.parse_meld(message)
                        tiles = meld.tiles
                        if len(tiles) == 4:
                            called_kan_indices.append(tiles[0])
                            tiles = tiles[1:4]

                        # closed kan
                        if meld.from_who == 0:
                            closed_hand.extend(tiles)
                        else:
                            melds.append(tiles)

                hand = closed_hand

                if melds:
                    hand += reduce(lambda z, y: z + y, melds)

                win_tile = int(tag.attrs['machi'])

                is_tsumo = winner == from_who
                is_riichi = 1 in yaku_list
                is_ippatsu = 2 in yaku_list
                is_chankan = 3 in yaku_list
                is_rinshan = 4 in yaku_list
                is_haitei = 5 in yaku_list
                is_houtei = 6 in yaku_list
                is_daburu_riichi = 21 in yaku_list
                is_dealer = winner == dealer
                is_renhou = 36 in yakuman_list
                is_tenhou = 37 in yakuman_list
                is_chiihou = 38 in yakuman_list

                dif = winner - dealer
                winds = [EAST, SOUTH, WEST, NORTH]
                player_wind = winds[dif]

                result = finished_hand.estimate_hand_value(hand,
                                                           win_tile,
                                                           is_tsumo=is_tsumo,
                                                           is_riichi=is_riichi,
                                                           is_dealer=is_dealer,
                                                           is_ippatsu=is_ippatsu,
                                                           is_rinshan=is_rinshan,
                                                           is_chankan=is_chankan,
                                                           is_haitei=is_haitei,
                                                           is_houtei=is_houtei,
                                                           is_daburu_riichi=is_daburu_riichi,
                                                           is_tenhou=is_tenhou,
                                                           is_renhou=is_renhou,
                                                           is_chiihou=is_chiihou,
                                                           round_wind=round_wind,
                                                           player_wind=player_wind,
                                                           called_kan_indices=called_kan_indices,
                                                           open_sets=melds,
                                                           dora_indicators=dora_indicators)

                if result['error']:
                    logger.error('Error with hand calculation: {}'.format(result['error']))
                    calculated_cost = 0
                    success = False
                else:
                    calculated_cost = result['cost']['main'] + result['cost']['additional'] * 2

                if success:
                    if result['fu'] != fu:
                        logger.error('Wrong fu: {} != {}'.format(result['fu'], fu))
                        success = False

                    if result['han'] != han:
                        logger.error('Wrong han: {} != {}'.format(result['han'], han))
                        success = False

                    if cost != calculated_cost:
                        logger.error('Wrong cost: {} != {}'.format(cost, calculated_cost))
                        success = False

                if not success:
                    logger.error('http://tenhou.net/0/?log={}&tw={}&ts={}'.format(log_id, winner, played_rounds - 1))
                    logger.error('Winner: {}, Dealer: {}'.format(winner, dealer))
                    logger.error('Hand: {}'.format(TilesConverter.to_one_line_string(hand)))
                    logger.error('Win tile: {}'.format(TilesConverter.to_one_line_string([win_tile])))
                    logger.error('Open sets: {}'.format(melds))
                    logger.error('Called kans: {}'.format(TilesConverter.to_one_line_string(called_kan_indices)))
                    logger.error('Our results: {}'.format(result))
                    logger.error('Tenhou results: {}'.format(tag.attrs))
                    logger.error('Dora: {}'.format(TilesConverter.to_one_line_string(dora_indicators)))
                    logger.error('')
                else:
                    successful_hand += 1

                total_hand += 1

        print('{},{}'.format(successful_hand, total_hand))


if __name__ == '__main__':
    main()
