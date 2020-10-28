from game.client import Client
from utils.general import make_random_letters_and_digit_string


class LocalClient(Client):
    seat = 0
    is_daburi = False
    is_ippatsu = False

    def __init__(self):
        super().__init__()
        self.id = make_random_letters_and_digit_string()

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
