from tenhou.client import TenhouClient
from utils.logger import set_up_logging


def connect_and_play():
    logger = set_up_logging()

    client = TenhouClient(logger)
    client.connect()

    try:
        was_auth = client.authenticate()

        if was_auth:
            client.start_game()
        else:
            client.end_game()
    except KeyboardInterrupt:
        logger.info("Ending the game...")
        client.end_game()
    except Exception as e:
        logger.exception("Unexpected exception", exc_info=e)
        logger.info("Ending the game...")
        client.end_game(False)
