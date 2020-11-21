from game.client import Client
from utils.general import make_random_letters_and_digit_string
from utils.logger import set_up_logging
from utils.settings_handler import settings


class LocalClient(Client):
    seat = 0
    is_daburi = False
    is_ippatsu = False
    is_rinshan = False

    def __init__(self, bot_config, print_logs, replay_name, game_count):
        super().__init__(bot_config)
        self.id = make_random_letters_and_digit_string()
        self.player.name = bot_config.name

        if print_logs:
            settings.LOG_PREFIX = self.player.name
            logger = set_up_logging(
                save_to_file=True, print_to_console=False, logger_name=self.player.name + str(game_count)
            )
            logger.info(f"Replay name: {replay_name}")
            self.player.init_logger(logger)

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
        self.is_rinshan = False

        self.table.erase_state()
