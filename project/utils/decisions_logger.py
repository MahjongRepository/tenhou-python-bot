import json
import logging
from copy import deepcopy

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
        if hasattr(message, "to_print"):
            message = message.to_print()

        if isinstance(message, dict):
            message = deepcopy(message)
            DecisionsLogger.serialize_dict_objects(message)
            logger.debug(json.dumps(message, indent=1))
        else:
            logger.debug(message)

    @staticmethod
    def serialize_dict_objects(d):
        for k, v in d.items():
            if isinstance(v, dict):
                DecisionsLogger.serialize_dict_objects(v)
            elif hasattr(v, "__str__") and v.__str__():
                d[k] = v.__str__()
