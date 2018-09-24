#!/usr/bin/env python3

from database import PeerReviewDB

import configparser
import logging
import sys


def configure_logger(log_file=None):
    handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    handlers.append(console_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        handlers.append(file_handler)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def main():
    config_file = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    configure_logger(config.get('database', 'log_file', fallback=None))

    db = PeerReviewDB(
        config['database']['db_file'],
        config.getboolean('database', 'override_db')
    )


if __name__ == '__main__':
    main()

