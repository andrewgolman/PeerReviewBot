import logging
import os.path
import sqlite3

from datatypes import *


def _convert_many_decorator(to_type):
    def decorator_impl(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return map(lambda v: to_type(*v), result)
        return wrapper
    return decorator_impl


def _convert_decorator(to_type):
    def decorator_impl(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return to_type(*result)
        return wrapper
    return decorator_impl


# TODO: user an orm library
class PeerReviewDB:
    logger = logging.getLogger('database')

    def __init__(self, db_file, override_db=False):
        self.db_file = db_file
        if not os.path.exists(db_file):
            PeerReviewDB.logger.info(
                'Creating database at {}'.format(os.path.abspath(self.db_file))
            )
            self._create_db()
        elif override_db:
            PeerReviewDB.logger.info(
                'Overriding database at {}'.format(os.path.abspath(self.db_file))
            )
            os.remove(db_file)
            self._create_db()
        else:
            PeerReviewDB.logger.info(
                'Using database found at {}'.format(os.path.abspath(self.db_file))
            )

    @_convert_decorator(User)
    def get_user(self, login):
        with self._create_connection() as db:
            return db.execute(
                'SELECT * FROM user WHERE login = ?',
                [login]
            ).fetchone()

    @_convert_decorator(Task)
    def get_task(self, name):
        with self._create_connection() as db:
            return db.execute(
                'SELECT * FROM task WHERE name = ?',
                [name]
            ).fetchone()

    @_convert_decorator(UserTask)
    def get_user_task(self, task_id):
        with self._create_connection() as db:
            return db.execute(
                'SELECT * FROM user_task WHERE rowid = ?',
                [task_id]
            ).fetchone()

    @_convert_decorator(Review)
    def get_review(self, reviewer, task_id):
        with self._create_connection() as db:
            return db.execute(
                'SELECT * FROM user_task WHERE reviewer = ? AND task_id = ?',
                [reviewer, task_id]
            ).fetchone()

    @_convert_many_decorator(User)
    def get_all_users(self):
        with self._create_connection() as db:
            return db.execute('SELECT * FROM user').fetchall()

    @_convert_many_decorator(Task)
    def get_all_tasks(self):
        with self._create_connection() as db:
            return db.execute('SELECT * FROM task').fetchall()

    @_convert_many_decorator(UserTask)
    def get_all_user_tasks(self):
        with self._create_connection() as db:
            return db.execute('SELECT * FROM user_task').fetchall()

    @_convert_many_decorator(Review)
    def get_all_reviewes(self):
        with self._create_connection() as db:
            return db.execute('SELECT * FROM review').fetchall()

    def add_user(self, user):
        with self._create_connection() as db:
            db.execute('INSERT INTO user VALUES (?)', (user.login,))

    def add_task(self, task):
        with self._create_connection() as db:
            db.execute('INSERT INTO task VALUES (?)', (task.name,))

    def add_user_task(self, user_task):
        with self._create_connection() as db:
            db.execute('''
                INSERT INTO user_task (user, task, url, status, timestamp)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    user_task.user,
                    user_task.task,
                    user_task.url,
                    user_task.status,
                    user_task.timestamp
                )
            )

    def add_review(self, review):
        with self._create_connection() as db:
            db.execute(
                'INSERT INTO review VALUES (?, ?, ?)',
                (
                    review.reviewer,
                    review.task_id,
                    review.status
                )
            )

    def remove_user(self, login):
        with self._create_connection() as db:
            db.execute('DELETE FROM user WHERE login = ?', (login,))

    def remove_task(self, name):
        with self._create_connection() as db:
            db.execute('DELETE FROM user WHERE name = ?', (name,))

    def remove_user_task(self, task_id):
        with self._create_connection() as db:
            db.execute('DELETE FROM user WHERE id = ?', (task_id,))

    def remove_review(self, reviewer, task_ib):
        with self._create_connection() as db:
            db.execute('''
                DELETE FROM user
                WHERE reviewer = ? AND task_id = ?
                ''', 
                (reviewer, task_id)
            )

    def _create_db(self):
        with self._create_connection() as db:
            db.execute('''
            CREATE TABLE user (
                login text PRIMARY KEY
            )''')
            db.execute('''
            CREATE TABLE task (
                name text PRIMARY KEY
            )''')
            db.execute('''
            CREATE TABLE user_task (
                id          int     PRIMARY KEY
                user        text    REFERENCES user(login),
                task        text    REFERENCES task(name),
                url         text,
                status      int,
                timestamp   int,
                UNIQUE(user, task)
            )''')
            db.execute('''
            CREATE TABLE review (
                reviewer text    REFERENCES user(login),
                task_id  int     REFERENCES user_task(id),
                status   int,
                PRIMARY KEY(reviewer, task_id)
            )''')

    def _create_connection(self):
        db = sqlite3.connect(self.db_file)
        db.set_trace_callback(PeerReviewDB.logger.debug)
        db.execute('PRAGMA foreign_keys = 1')
        return db

