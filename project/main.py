import logging

from tenhou.main import connect_and_play

def set_up_logging():
    logger = logging.getLogger('tenhou')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    ch.setFormatter(formatter)

    logger.addHandler(ch)


def main():
    set_up_logging()

    connect_and_play()


if __name__ == '__main__':
    main()