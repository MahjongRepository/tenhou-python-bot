import logging

logger = logging.getLogger('ai')


class DecisionsLogger:

    @staticmethod
    def debug(message_id, message='', context=None, print_log=True):
        if not print_log:
            return

        logger.debug('id={}'.format(message_id))

        if message:
            logger.debug(message)

        if context:
            if type(context) == list:
                for x in context:
                    logger.debug(x)
            else:
                logger.debug(context)
