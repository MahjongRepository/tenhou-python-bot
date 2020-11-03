from game.client import Client
from utils.general import make_random_letters_and_digit_string


class LocalClient(Client):
    seat = 0
    is_daburi = False
    is_ippatsu = False

    def __init__(self, bot_config):
        super().__init__(bot_config)
        self.id = make_random_letters_and_digit_string()
        self.player.name = bot_config.name

    def connect(self):
        pass

    def authenticate(self):
        pass

    def start_game(self):
        pass

    def end_game(self):
        pass

    def erase_state(self):
        self.is_daburi = False
        self.is_ippatsu = False
