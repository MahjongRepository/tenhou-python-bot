import logging
import re
from threading import Thread
from time import sleep
from urllib.parse import quote

from mahjong.ai.shanten import Shanten
from mahjong.client import Client
from mahjong.tile import TilesConverter
from tenhou import settings
from tenhou.decoder import TenhouDecoder

logger = logging.getLogger('tenhou')


class TenhouClient(Client):
    socket = None
    game_is_continue = True
    keep_alive_thread = None

    decoder = TenhouDecoder()

    def __init__(self, socket):
        super().__init__()
        self.socket = socket

    def authenticate(self):
        self._send_message('<HELO name="{0}" tid="f0" sx="M" />'.format(quote(settings.USER_ID)))
        auth_message = self._read_message()

        auth_string = self.decoder.parse_auth_string(auth_message)
        if not auth_string:
            return False

        auth_token = self.decoder.generate_auth_token(auth_string)

        self._send_message('<AUTH val="{0}"/>'.format(auth_token))
        self._send_message(self._pxr_tag())

        message = self._read_message()
        if '<ln' in message:
            self._send_keep_alive_ping()
            logger.info('Successfully authenticated')
            return True
        else:
            return False

    def start_the_game(self):
        log_link = ''
        game_id = ''

        game_started = False
        self._send_message('<JOIN t="{0}" />'.format(settings.GAME_TYPE))
        logger.info('Looking for the game...')

        while not game_started:
            sleep(1)

            messages = self._get_multiple_messages()

            for message in messages:

                if '<rejoin' in message:
                    # game wasn't found, continue to wait
                    self._send_message('<JOIN t="{0},r" />'.format(settings.GAME_TYPE))

                if '<go' in message:
                    self._send_message('<GOK />')
                    self._send_message('<NEXTREADY />')

                if '<taikyoku' in message:
                    game_started = True
                    game_id, seat = self.decoder.parse_log_link(message)
                    log_link = 'http://tenhou.net/0/?log={0}&tw={1}'.format(game_id, seat)
                    self.statistics.game_id = game_id

                if '<un' in message:
                    values = self.decoder.parse_names_and_ranks(message)
                    self.table.set_players_names_and_ranks(values)

                if '<ln' in message:
                    self._send_message(self._pxr_tag())

        logger.info('Game started')
        logger.info('Log: {0}'.format(log_link))
        logger.info('Players: {0}'.format(self.table.players))

        main_player = self.table.get_main_player()

        while self.game_is_continue:
            sleep(1)

            messages = self._get_multiple_messages()

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
                    logger.info('Players: {0}'.format(self.table.get_players_sorted_by_scores()))

                # draw and discard
                if '<t' in message:
                    tile = self.decoder.parse_tile(message)

                    if not main_player.in_riichi:
                        self.draw_tile(tile)
                        sleep(1)

                        logger.info('Hand: {0}'.format(TilesConverter.to_one_line_string(main_player.tiles)))

                        tile = self.discard_tile()

                    if 't="16"' in message:
                        # we win by self draw (tsumo)
                        self._send_message('<N type="7" />')
                    else:
                        # let's call riichi and after this discard tile
                        if main_player.in_tempai and not main_player.in_riichi:
                            self._send_message('<REACH hai="{0}" />'.format(tile))
                            sleep(2)
                            main_player.in_riichi = True

                        # tenhou format: <D p="133" />
                        self._send_message('<D p="{0}"/>'.format(tile))

                # new dora indicator after kan
                if '<dora' in message:
                    tile = self.decoder.parse_dora_indicator(message)
                    self.table.add_dora_indicator(tile)
                    logger.info('New dora indicator: {0}'.format(tile))

                # the end of round
                if 'agari' in message or 'ryuukyoku' in message:
                    sleep(2)
                    self._send_message('<NEXTREADY />')

                open_sets = ['t="1"', 't="2"', 't="3"', 't="4"', 't="5"']
                if any(i in message for i in open_sets):
                    sleep(1)
                    self._send_message('<N />')

                # set call
                if '<n who=' in message:
                    meld = self.decoder.parse_meld(message)
                    self.call_meld(meld)
                    logger.info('Meld: {0}, who {1}'.format(meld.type, meld.who))

                # other players discards: <e, <f, <g + tile number
                match_discard = re.match(r"^<[efg]+\d.*", message)
                if match_discard:
                    # we win by other player's discard
                    if 't="8"' in message:
                        self._send_message('<N type="6" />')

                    tile = self.decoder.parse_tile(message)

                    if '<e' in message:
                        player_seat = 1
                    elif '<f' in message:
                        player_seat = 2
                    else:
                        player_seat = 3

                    self.enemy_discard(player_seat, tile)

                if 'owari' in message:
                    values = self.decoder.parse_final_scores_and_uma(message)
                    self.table.set_players_scores(values['scores'], values['uma'])

                if '<prof' in message:
                    self.game_is_continue = False

        logger.info('Final results: {0}'.format(self.table.get_players_sorted_by_scores()))

        self.end_the_game()

        # sometimes log is available just after the game
        # let's wait one minute before the statistics update
        sleep(60)
        result = self.statistics.send_statistics()
        logger.info('Statistics sent: {0}'.format(result))

    def end_the_game(self):
        self._send_message('<BYE />')
        self.socket.close()

        self.keep_alive_thread.join()

        logger.info('End of the game')

    def _send_message(self, message):
        # tenhou required the empty byte in the end of each sending message
        logger.debug('Send: {0}'.format(message))
        message += '\0'
        self.socket.sendall(message.encode())

    def _read_message(self):
        message = self.socket.recv(1024)
        logger.debug('Get: {0}'.format(message.decode('utf-8').replace('\x00', ' ')))

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
        if settings.USER_ID == 'NoName':
            return '<PXR V="1" />'
        else:
            return '<PXR V="9" />'
