import json
import logging
from copy import deepcopy

from mahjong.meld import Meld
from mahjong.tile import TilesConverter

logger = logging.getLogger("ai")


class DecisionsLogger:
    @staticmethod
    def debug(message_id, message="", context=None):
        logger.debug("id={}".format(message_id))

        if message:
            DecisionsLogger.log_message(message)

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

    def serialize(self):
        return {
            "type": self.type,
            "tiles_string": TilesConverter.to_one_line_string(self.tiles),
            "tiles": self.tiles,
        }
