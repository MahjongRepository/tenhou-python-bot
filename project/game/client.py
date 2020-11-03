from game.table import Table


class Client:
    table = None

    def __init__(self, bot_config=None):
        self.table = Table(bot_config)

    def connect(self):
        raise NotImplementedError()

    def authenticate(self):
        raise NotImplementedError()

    def start_game(self):
        raise NotImplementedError()

    def end_game(self):
        raise NotImplementedError()

    @property
    def player(self):
        return self.table.player
