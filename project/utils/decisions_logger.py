import json
import logging
from copy import deepcopy

from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from utils.settings_handler import settings

logger = logging.getLogger("bot")


class DecisionsLogger:
    @staticmethod
    def debug(message_id, message="", context=None):
        if not settings.PRINT_LOGS:
            return None

        logger.debug(f"id={message_id}")

        if message:
            logger.debug(f"msg={message}")

        if context:
            if isinstance(context, list):
                for x in context:
                    DecisionsLogger.log_message(x)
            else:
                DecisionsLogger.log_message(context)

    @staticmethod
    def log_message(message):
        if hasattr(message, "serialize"):
            message = message.serialize()

        if isinstance(message, dict):
            message = deepcopy(message)
            DecisionsLogger.serialize_dict_objects(message)
            logger.debug(json.dumps(message))
        else:
            logger.debug(message)

    @staticmethod
    def serialize_dict_objects(d):
        for k, v in d.items():
            if isinstance(v, dict):
                DecisionsLogger.serialize_dict_objects(v)
            elif isinstance(v, list):
                for i in range(len(v)):
                    if isinstance(v, dict):
                        DecisionsLogger.serialize_dict_objects(v)
                    elif hasattr(v[i], "serialize"):
                        v[i] = v[i].serialize()
            elif hasattr(v, "serialize"):
                d[k] = v.serialize()


class MeldPrint(Meld):
    """
    Wrapper to be able use mahjong package MeldPrint object in our loggers.
    """

    def __str__(self):
        meld_type_str = self.type
        if meld_type_str == self.KAN:
            meld_type_str += f" open={self.opened}"
        return f"Type: {meld_type_str}, Tiles: {TilesConverter.to_one_line_string(self.tiles)} {self.tiles}"

    def serialize(self):
        return {
            "type": self.type,
            "tiles_string": TilesConverter.to_one_line_string(self.tiles),
            "tiles": self.tiles,
        }
