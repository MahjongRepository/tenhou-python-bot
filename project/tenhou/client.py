import logging
from threading import Thread
from time import sleep

from bs4 import BeautifulSoup

from mahjong.hand import PlayerHand
from mahjong.table import Table
from tenhou.decoder import TenhouDecoder

logger = logging.getLogger('tenhou')


class TenhouClient(object):
    socket = None
    game_is_continue = True
    keep_alive_thread = None

    hand = PlayerHand()
    table = Table()
    decoder = TenhouDecoder(table, hand)

    def __init__(self, socket):
        self.socket = socket

    def authenticate(self):
        self._send_message('<HELO name="NoName" tid="f0" sx="M" />')
        auth_message = self._read_message()

        # I know about regexp, but I think using BeautifulSoup for parsing will be more effective
        soup = BeautifulSoup(auth_message, 'html.parser')
        soup = soup.find('helo')
        if soup and 'auth' in soup.attrs:
            auth_string = soup.attrs['auth']
        else:
            return False

        auth_token = self._generate_auth_token(auth_string)

        self._send_message('<AUTH val="{0}"/>'.format(auth_token))
        self._send_message('<PXR V="0" />')
        self._send_message('<PXR V="1" />')

        message = self._read_message()
        if '<ln' in message:
            self._send_keep_alive_ping()
            logger.info('Successfully authenticated')
            return True
        else:
            return False

    def start_the_game(self):
        game_started = False
        self._send_message('<JOIN t="0,1" />')
        logger.info('Began looking for the game')

        while not game_started:
            sleep(1)

            messages = self._get_multiple_messages()

            for message in messages:

                if '<rejoin' in message:
                    # game wasn't found, continue to wait
                    self._send_message('<JOIN t="0,1,r" />')

                if '<go' in message:
                    self._send_message('<GOK />')
                    self._send_message('<NEXTREADY />')

                if '<taikyoku' in message:
                    game_started = True
                    logger.info('Game started')
                    self.decoder.decode_log_link(message)

        while self.game_is_continue:
            sleep(1)

            messages = self._get_multiple_messages()

            for message in messages:

                if '<init' in message:
                    self.decoder.decode_initial_values(message)

                # draw and discard
                if '<t' in message:
                    self._draw_tile(message)
                    sleep(1)
                    self._discard_tile()

                # the end of round
                if 'agari' in message or 'ryuukyoku' in message:
                    logger.info('Player 1')
                    logger.info(self.table.get_player(1))

                    logger.info('Player 2')
                    logger.info(self.table.get_player(2))

                    logger.info('Player 3')
                    logger.info(self.table.get_player(3))

                    sleep(2)
                    self._send_message('<NEXTREADY />')

                open_sets = ['t="1"', 't="2"', 't="3"', 't="4"', 't="5"']
                if any(i in message for i in open_sets):
                    sleep(1)
                    result = self.hand.should_set_be_called(message)
                    if result:
                        pass
                    else:
                        self._send_message('<N />')

                # set call
                if '<n who=' in message:
                    self.decoder.decode_meld(message)

                if '<prof' in message:
                    self.game_is_continue = False

                other_players_discards = ['<e', '<f', '<g']
                if any(i in message for i in other_players_discards):
                    tile = self.decoder.decode_tile(message)

                    if '<e' in message:
                        player_number = 1
                    elif '<f' in message:
                        player_number = 2
                    else:
                        player_number = 3

                    self.table.get_player(player_number).add_discard(tile)

        self.end_the_game()

    def end_the_game(self):
        self._send_message('<BYE />')
        self.socket.close()

        self.keep_alive_thread.join()

        logger.info('End of the game')

    def _draw_tile(self, tenhou_string):
        tile = self.decoder.decode_tile(tenhou_string)
        self.hand.draw_tile(tile)

    def _discard_tile(self):
        tile = self.hand.discard_tile()

        # tenhou format: <D p="133" />
        self._send_message('<D p="{0}"/>'.format(tile))

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

    def _generate_auth_token(self, auth_string):
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

