# -*- coding: utf-8 -*-
import datetime
import logging
import socket
from threading import Thread
from time import sleep
from urllib.parse import quote

import re

from mahjong.constants import DISPLAY_WINDS
from utils.settings_handler import settings
from mahjong.client import Client
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from tenhou.decoder import TenhouDecoder

logger = logging.getLogger('tenhou')


class TenhouClient(Client):
    socket = None
    game_is_continue = True
    looking_for_game = True
    keep_alive_thread = None

    decoder = TenhouDecoder()

    _count_of_empty_messages = 0

    def __init__(self, socket_object):
        super(TenhouClient, self).__init__()
        self.socket = socket_object

    def authenticate(self):
        self._send_message('<HELO name="{}" tid="f0" sx="M" />'.format(quote(settings.USER_ID)))
        auth_message = ''

        # we need to wait to get auth message
        # sometimes it can be a couple of empty messages before real auth message
        continue_reading = True
        counter = 0
        while continue_reading:
            auth_message = self._read_message()
            if auth_message:
                continue_reading = False
            else:
                counter += 1

            # to avoid infinity loop
            if counter > 20:
                continue_reading = False

        if not auth_message:
            logger.info("Auth message wasn't received")
            return False

        auth_string = self.decoder.parse_auth_string(auth_message)
        if not auth_string:
            logger.info('We obtain auth string')
            return False

        auth_token = self.decoder.generate_auth_token(auth_string)

        self._send_message('<AUTH val="{}"/>'.format(auth_token))
        self._send_message(self._pxr_tag())

        # sometimes tenhou send an empty tag after authentication (in tournament mode)
        # and bot thinks that he was not auth
        # to prevent it lets wait a little bit
        # and lets read a group of tags
        continue_reading = True
        counter = 0
        authenticated = False
        while continue_reading:
            messages = self._get_multiple_messages()
            for message in messages:
                if '<ln' in message:
                    authenticated = True
                    continue_reading = False

            # to avoid infinity loop
            if counter > 20:
                continue_reading = False

        if authenticated:
            self._send_keep_alive_ping()
            logger.info('Successfully authenticated')
            return True
        else:
            logger.info('Failed to authenticate')
            return False

    def start_game(self):
        log_link = ''

        if settings.LOBBY != '0':
            if settings.IS_TOURNAMENT:
                logger.info('Go to the tournament lobby: {}'.format(settings.LOBBY))
                self._send_message('<CS lobby="{}" />'.format(settings.LOBBY))
                sleep(2)
                self._send_message('<DATE />')
            else:
                logger.info('Go to the lobby: {}'.format(settings.LOBBY))
                self._send_message('<CHAT text="{}" />'.format(quote('/lobby {}'.format(settings.LOBBY))))
                sleep(2)

        game_type = '{},{}'.format(settings.LOBBY, settings.GAME_TYPE)

        if not settings.IS_TOURNAMENT:
            self._send_message('<JOIN t="{}" />'.format(game_type))
            logger.info('Looking for the game...')

        start_time = datetime.datetime.now()

        while self.looking_for_game:
            sleep(1)

            messages = self._get_multiple_messages()

            for message in messages:
                if '<rejoin' in message:
                    # game wasn't found, continue to wait
                    self._send_message('<JOIN t="{},r" />'.format(game_type))

                if '<go' in message:
                    self._send_message('<GOK />')
                    self._send_message('<NEXTREADY />')

                if '<taikyoku' in message:
                    self.looking_for_game = False
                    game_id, seat = self.decoder.parse_log_link(message)
                    log_link = 'http://tenhou.net/0/?log={}&tw={}'.format(game_id, seat)
                    self.statistics.game_id = game_id

                if '<un' in message:
                    values = self.decoder.parse_names_and_ranks(message)
                    self.table.set_players_names_and_ranks(values)

                if '<ln' in message:
                    self._send_message(self._pxr_tag())

            current_time = datetime.datetime.now()
            time_difference = current_time - start_time

            if time_difference.seconds > 60 * settings.WAITING_GAME_TIMEOUT_MINUTES:
                break

        # we wasn't able to find the game in timeout minutes
        # sometimes it happens and we need to end process
        # and try again later
        if self.looking_for_game:
            logger.error('Game is not started. Can\'t find the game')
            self.end_game()
            return

        logger.info('Game started')
        logger.info('Log: {}'.format(log_link))
        logger.info('Players: {}'.format(self.table.players))

        main_player = self.table.get_main_player()

        # tiles to work with meld calling
        tile_to_discard = None
        meld_tile = None
        shanten = 7

        while self.game_is_continue:
            sleep(1)

            messages = self._get_multiple_messages()

            if not messages:
                self._count_of_empty_messages += 1
            else:
                # we had set to zero counter
                self._count_of_empty_messages = 0

            for message in messages:
                if '<init' in message:
                    values = self.decoder.parse_initial_values(message)
                    self.table.init_round(
                        values['round_number'],
                        values['count_of_honba_sticks'],
                        values['count_of_riichi_sticks'],
                        values['dora_indicator'],
                        values['dealer'],
                        values['scores'],
                    )

                    tiles = self.decoder.parse_initial_hand(message)
                    self.table.init_main_player_hand(tiles)

                    logger.info(self.table.__str__())
                    logger.info('Players: {}'.format(self.table.get_players_sorted_by_scores()))
                    logger.info('Dealer: {}'.format(self.table.get_player(values['dealer'])))
                    logger.info('Round  wind: {}'.format(DISPLAY_WINDS[self.table.round_wind]))
                    logger.info('Player wind: {}'.format(DISPLAY_WINDS[main_player.player_wind]))

                # draw and discard
                if '<t' in message:
                    tile = self.decoder.parse_tile(message)

                    if not main_player.in_riichi:
                        logger.info('Hand: {}'.format(main_player.format_hand_for_print(tile)))

                        self.draw_tile(tile)
                        sleep(1)

                        tile = self.discard_tile()

                        logger.info('Discard: {}'.format(TilesConverter.to_one_line_string([tile])))

                    if 't="16"' in message:
                        # we win by self draw (tsumo)
                        self._send_message('<N type="7" />')
                    else:
                        # let's call riichi and after this discard tile
                        if main_player.can_call_riichi():
                            self._send_message('<REACH hai="{}" />'.format(tile))
                            sleep(2)
                            main_player.in_riichi = True

                        # tenhou format: <D p="133" />
                        self._send_message('<D p="{}"/>'.format(tile))

                        logger.info('Remaining tiles: {}'.format(self.table.count_of_remaining_tiles))

                # new dora indicator after kan
                if '<dora' in message:
                    tile = self.decoder.parse_dora_indicator(message)
                    self.table.add_dora_indicator(tile)
                    logger.info('New dora indicator: {}'.format(TilesConverter.to_one_line_string([tile])))

                if '<reach' in message and 'step="2"' in message:
                    who_called_riichi = self.decoder.parse_who_called_riichi(message)
                    self.enemy_riichi(who_called_riichi)
                    logger.info('Riichi called by {} player'.format(who_called_riichi))

                # the end of round
                if 'agari' in message or 'ryuukyoku' in message:
                    sleep(2)
                    self._send_message('<NEXTREADY />')

                # for now I'm not sure about what sets was suggested to call with this numbers
                # will find it out later
                not_allowed_open_sets = ['t="2"', 't="3"', 't="5"', 't="7"']
                if any(i in message for i in not_allowed_open_sets):
                    sleep(1)
                    self._send_message('<N />')

                # set was called
                if '<n who=' in message:
                    meld = self.decoder.parse_meld(message)
                    logger.info('Meld: {} by {}'.format(meld, meld.who))

                    # tenhou confirmed that we called a meld
                    # we had to do discard after this
                    if meld.who == 0:
                        logger.info('With hand: {}'.format(main_player.format_hand_for_print(meld_tile)))
                        logger.info('Discard tile after called meld: {}'.format(
                            TilesConverter.to_one_line_string([tile_to_discard])))
                        self._send_message('<D p="{}"/>'.format(tile_to_discard))
                        self.player.discard_tile(tile_to_discard)

                        self.player.tiles.append(meld_tile)
                        self.player.ai.previous_shanten = shanten

                    self.table.add_called_meld(meld, meld.who)

                win_suggestions = ['t="8"', 't="9"', 't="12"', 't="13"']
                # we win by other player's discard
                if any(i in message for i in win_suggestions):
                    sleep(1)
                    self._send_message('<N type="6" />')

                # other players discards: <e, <f, <g + tile number
                match_discard = re.match(r"^<[efg]+\d.*", message)
                if match_discard:
                    tile = self.decoder.parse_tile(message)

                    if '<e' in message:
                        player_seat = 1
                    elif '<f' in message:
                        player_seat = 2
                    else:
                        player_seat = 3

                    self.table.enemy_discard(tile, player_seat)

                    if 't="1"' in message or 't="4"' in message:
                        is_kamicha_discard = False
                        # t="1" - call pon set
                        # t="4" - call chi set
                        if 't="4"' in message:
                            is_kamicha_discard = True

                        meld, tile_to_discard, shanten = self.player.try_to_call_meld(tile, is_kamicha_discard)
                        if meld:
                            meld_tile = tile

                            meld_type = '1'
                            if meld.type == Meld.CHI:
                                # yeah it is 3, not 4
                                # because of tenhou protocol
                                meld_type = '3'

                            tiles = meld.tiles
                            tiles.remove(meld_tile)

                            # try to call a meld
                            self._send_message('<N type="{}" hai0="{}" hai1="{}" />'.format(
                                meld_type,
                                tiles[0],
                                tiles[1]
                            ))
                        else:
                            sleep(1)
                            self._send_message('<N />')

                if 'owari' in message:
                    values = self.decoder.parse_final_scores_and_uma(message)
                    self.table.set_players_scores(values['scores'], values['uma'])

                if '<prof' in message:
                    self.game_is_continue = False

            if self._count_of_empty_messages > 10:
                logger.error('Tenhou send empty messages to us. Probably we did something wrong with protocol')
                self.end_game(False)
                return

        logger.info('Final results: {}'.format(self.table.get_players_sorted_by_scores()))

        # we need to finish the game, and only after this try to send statistics
        # if order will be different, tenhou will return 404 on log download endpoint
        self.end_game()

        # sometimes log is not available just after the game
        # let's wait one minute before the statistics update
        if settings.STAT_SERVER_URL:
            sleep(60)
            result = self.statistics.send_statistics()
            logger.info('Statistics sent: {}'.format(result))

    def end_game(self, success=True):
        self.game_is_continue = False
        self._send_message('<BYE />')

        if self.keep_alive_thread:
            self.keep_alive_thread.join()

        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

        if success:
            logger.info('End of the game')
        else:
            logger.error('Game was ended without of success')

    def _send_message(self, message):
        # tenhou requires an empty byte in the end of each sending message
        logger.debug('Send: {}'.format(message))
        message += '\0'
        self.socket.sendall(message.encode())

    def _read_message(self):
        message = self.socket.recv(1024)
        logger.debug('Get: {}'.format(message.decode('utf-8').replace('\x00', ' ')))

        message = message.decode('utf-8')
        # sometimes tenhou send messages in lower case, sometime in upper case, let's unify the behaviour
        message = message.lower()

        return message

    def _get_multiple_messages(self):
        # tenhou can send multiple messages in one request
        messages = self._read_message()
        messages = messages.split('\x00')
        # last message always is empty after split, so let's exclude it
        messages = messages[0:-1]

        return messages

    def _send_keep_alive_ping(self):
        def send_request():
            while self.game_is_continue:
                self._send_message('<Z />')
                sleep(15)

        self.keep_alive_thread = Thread(target=send_request)
        self.keep_alive_thread.start()

    def _pxr_tag(self):
        # I have no idea why we need to send it, but better to do it
        if settings.IS_TOURNAMENT:
            return '<PXR V="-1" />'

        if settings.USER_ID == 'NoName':
            return '<PXR V="1" />'
        else:
            return '<PXR V="9" />'
