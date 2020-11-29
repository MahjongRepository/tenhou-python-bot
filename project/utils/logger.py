import datetime
import hashlib
import logging
import os
from logging.handlers import SysLogHandler

from utils.settings_handler import settings

LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColoredFormatter(logging.Formatter):
    """
    Apply only to the console handler.
    """

    green = "\u001b[32m"
    cyan = "\u001b[36m"
    reset = "\u001b[0m"

    def format(self, record):
        format_style = self._fmt

        if record.getMessage().startswith("id="):
            format_style = f"{ColoredFormatter.green}{format_style}{ColoredFormatter.reset}"
        if record.getMessage().startswith("msg="):
            format_style = f"{ColoredFormatter.cyan}{format_style}{ColoredFormatter.reset}"

        formatter = logging.Formatter(format_style)
        return formatter.format(record)


def set_up_logging(save_to_file=True, print_to_console=True, logger_name="bot"):
    """
    Logger for tenhou communication and AI output
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if print_to_console:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    log_prefix = settings.LOG_PREFIX
    if not log_prefix:
        log_prefix = hashlib.sha1(settings.USER_ID.encode("utf-8")).hexdigest()[:5]

    if save_to_file:
        logs_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "logs")
        if not os.path.exists(logs_directory):
            os.mkdir(logs_directory)

        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

        # we need it to distinguish different bots logs (if they were run in the same time)
        file_name = "{}_{}.log".format(log_prefix, datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S"))

        fh = logging.FileHandler(os.path.join(logs_directory, file_name), encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    if settings.PAPERTRAIL_HOST_AND_PORT:
        syslog = SysLogHandler(address=settings.PAPERTRAIL_HOST_AND_PORT)
        game_id = f"BOT_{log_prefix}"

        formatter = ColoredFormatter(f"%(asctime)s {game_id}: %(message)s", datefmt=DATE_FORMAT)
        syslog.setFormatter(formatter)

        logger.addHandler(syslog)

    return logger
