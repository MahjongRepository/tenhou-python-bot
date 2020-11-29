"""
Endpoint to run bot. It will play a game on tenhou.net
"""
import importlib
from optparse import OptionParser

from tenhou.main import connect_and_play
from utils.settings_handler import settings


def parse_args_and_set_up_settings():
    parser = OptionParser()

    parser.add_option(
        "-u",
        "--user_id",
        type="string",
        default=settings.USER_ID,
        help="Tenhou's user id. Example: IDXXXXXXXX-XXXXXXXX. Default is {0}".format(settings.USER_ID),
    )
    parser.add_option(
        "-g",
        "--game_type",
        type="string",
        default=settings.GAME_TYPE,
        help="The game type in Tenhou.net. Examples: 1 or 9. Default is {0}".format(settings.GAME_TYPE),
    )
    parser.add_option(
        "-l",
        "--lobby",
        type="string",
        default=settings.LOBBY,
        help="Lobby to play. Default is {0}".format(settings.LOBBY),
    )
    parser.add_option(
        "-t",
        "--timeout",
        type="int",
        default=settings.WAITING_GAME_TIMEOUT_MINUTES,
        help="How much minutes bot will looking for a game. "
        "If game is not started in timeout, script will be ended. "
        "Default is {0}".format(settings.WAITING_GAME_TIMEOUT_MINUTES),
    )
    parser.add_option(
        "-c",
        "--championship",
        type="string",
        help="Tournament lobby to play.",
    )
    parser.add_option(
        "-s",
        "--settings",
        type="string",
        default=None,
        help="Settings file name (without path, just file name without extension)",
    )

    opts, _ = parser.parse_args()

    settings.USER_ID = opts.user_id
    settings.GAME_TYPE = opts.game_type
    settings.LOBBY = opts.lobby
    settings.WAITING_GAME_TIMEOUT_MINUTES = opts.timeout

    if opts.settings:
        module = importlib.import_module(f"settings.{opts.settings}")
        for key, value in vars(module).items():
            # let's use only upper case settings
            if key.isupper():
                settings.__setattr__(key, value)

    if opts.championship:
        settings.IS_TOURNAMENT = True
        settings.LOBBY = opts.championship


def main():
    parse_args_and_set_up_settings()

    if settings.SENTRY_URL:
        import sentry_sdk

        sentry_sdk.init(
            settings.SENTRY_URL,
            traces_sample_rate=1.0,
        )

    connect_and_play()


if __name__ == "__main__":
    main()
