import json
import logging
from copy import deepcopy

from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from utils.settings_handler import settings


class DecisionsLogger:
    logger = logging.getLogger()

    def debug(self, message_id, message="", context=None):
        if not settings.PRINT_LOGS:
            return None

        self.logger.debug(f"id={message_id}")

        if message:
            self.logger.debug(f"msg={message}")

        if context:
            if isinstance(context, list):
                for x in context:
                    self.log_message(x)
            else:
                self.log_message(context)

    def log_message(self, message):
        if hasattr(message, "serialize"):
            message = message.serialize()

        if isinstance(message, dict):
            message = deepcopy(message)
            self.serialize_dict_objects(message)
            self.logger.debug(json.dumps(message))
        else:
            self.logger.debug(message)

    def serialize_dict_objects(self, d):
        for k, v in d.items():
            if isinstance(v, dict):
                self.serialize_dict_objects(v)
            elif isinstance(v, list):
                for i in range(len(v)):
                    if isinstance(v, dict):
                        self.serialize_dict_objects(v)
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
