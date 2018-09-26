#!/usr/bin/env python3

from database import PeerReviewDB
from datatypes import User, Task, UserTask, Review

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


def test_user(database):
    # database is empty
    user0 = User('user0')
    user1 = User('user1')

    database.add_user(user0)
    database.add_user(user1)

    assert database.get_user('user0') == user0
    assert database.get_user('user1') == user1
    assert database.get_user('user2') is None
    
    assert set(database.get_all_users()) == set([user0, user1])

    database.remove_user('user0')

    assert database.get_all_users() == [user1]


def test_task(database):
    # user1 is still in the database from the previous test
    task0 = Task('task0')
    task1 = Task('task1')

    database.add_task(task0)
    database.add_task(task1)

    assert database.get_task('task0') == task0
    assert database.get_task('task1') == task1
    assert database.get_task('task2') is None
    
    assert set(database.get_all_tasks()) == set([task0, task1])

    database.remove_task('task0')

    assert database.get_all_tasks() == [task1]


def test_user_task(database):
    # user1 and task1 are still in the database from the previous two test
    database.add_user(User('user0'))
    database.add_task(Task('task0'))

    user_task0 = UserTask('user0', 'task0', '#', 0, 0)
    user_task1 = UserTask('user1', 'task1', '$', 0, 0)

    database.add_user_task(user_task0)
    database.add_user_task(user_task1)

    assert database.get_user_task('user0', 'task0') == user_task0
    assert database.get_user_task('user1', 'task1') == user_task1
    assert database.get_user_task('user0', 'task1') is None
    
    assert set(database.get_all_user_tasks()) == set([user_task0, user_task1])

    database.remove_user_task('user0', 'task0')

    assert database.get_all_user_tasks() == [user_task1]


def test_review(database):
    # user0, user1, task0, task1 and user_task1
    # are still in the database from the previous two test
    database.add_user_task(UserTask('user0', 'task0', '#', 0, 0))

    review0 = Review('user0', 'user1', 'task1', 0)
    review1 = Review('user1', 'user0', 'task0', 0)

    database.add_review(review0)
    database.add_review(review1)

    assert database.get_review('user0', 'user1', 'task1') == review0
    assert database.get_review('user1', 'user0', 'task0') == review1
    assert database.get_review('user0', 'user1', 'task0') is None
    
    assert set(database.get_all_reviews()) == set([review0, review1])

    database.remove_review('user0', 'user1', 'task1')

    assert database.get_all_reviews() == [review1]


def main():
    config_file = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    configure_logger(config.get('database', 'log_file', fallback=None))

    db = PeerReviewDB(
        config['database']['db_file'],
        config.getboolean('database', 'override_db')
    )

    test_user(db)
    test_task(db)
    test_user_task(db)
    test_review(db)


if __name__ == '__main__':
    main()

