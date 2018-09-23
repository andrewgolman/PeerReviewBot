#!/usr/bin/env python3

from database import PeerReviewDB

import configparser
import logging
import logging.config
import sys


def configure_logger(log_file=None):
    logger = PeerReviewDB.logger
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def main():
    config_file = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    configure_logger(config.get('database', 'log_file', fallback=None))

    db = PeerReviewDB(config['database']['db_file'])


if __name__ == '__main__':
    main()
