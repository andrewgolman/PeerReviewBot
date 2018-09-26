import logging
import os.path
import sqlite3

from datatypes import User, Task, UserTask, Review


def _convert_list_decorator(to_type):
    def decorator_impl(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return list(map(lambda v: to_type(*v), result))
        return wrapper
    return decorator_impl


def _convert_decorator(to_type):
    def decorator_impl(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is not None:
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
                (login,)
            ).fetchone()

    @_convert_decorator(Task)
    def get_task(self, name):
        with self._create_connection() as db:
            return db.execute(
                'SELECT * FROM task WHERE name = ?',
                (name,)
            ).fetchone()

    @_convert_decorator(UserTask)
    def get_user_task(self, user, task):
        with self._create_connection() as db:
            return db.execute('''
                SELECT * FROM user_task
                WHERE user = ? AND task = ?
                ''',
                (user, task)
            ).fetchone()

    @_convert_decorator(Review)
    def get_review(self, reviewer, reviewee, task):
        with self._create_connection() as db:
            return db.execute('''
                SELECT * FROM review
                WHERE reviewer = ? AND reviewee = ? AND task = ?
                ''',
                (reviewer, reviewee, task)
            ).fetchone()

    @_convert_list_decorator(User)
    def get_all_users(self):
        with self._create_connection() as db:
            return db.execute('SELECT * FROM user').fetchall()

    @_convert_list_decorator(Task)
    def get_all_tasks(self):
        with self._create_connection() as db:
            return db.execute('SELECT * FROM task').fetchall()

    @_convert_list_decorator(UserTask)
    def get_all_user_tasks(self):
        with self._create_connection() as db:
            return db.execute('SELECT * FROM user_task').fetchall()

    @_convert_list_decorator(Review)
    def get_all_reviews(self):
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
            db.execute(
                'INSERT INTO user_task VALUES (?, ?, ?, ?, ?)',
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
                'INSERT INTO review VALUES (?, ?, ?, ?)',
                (
                    review.reviewer,
                    review.reviewee,
                    review.task,
                    review.status
                )
            )

    def remove_user(self, login):
        with self._create_connection() as db:
            db.execute('DELETE FROM user WHERE login = ?', (login,))

    def remove_task(self, name):
        with self._create_connection() as db:
            db.execute('DELETE FROM task WHERE name = ?', (name,))

    def remove_user_task(self, user, task):
        with self._create_connection() as db:
            db.execute('''
                DELETE FROM user_task
                WHERE user = ? AND task = ?
                ''',
                (user, task)
            )

    def remove_review(self, reviewer, reviewee, task):
        with self._create_connection() as db:
            db.execute('''
                DELETE FROM review
                WHERE reviewer = ? AND reviewee = ? AND task = ?
                ''', 
                (reviewer, reviewee, task)
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
                user        text    REFERENCES user(login),
                task        text    REFERENCES task(name),
                url         text,
                status      int,
                timestamp   int,
                PRIMARY KEY (user, task)
            )''')
            db.execute('''
            CREATE TABLE review (
                reviewer text    REFERENCES user(login),
                reviewee text,
                task     text,
                status   int,
                PRIMARY KEY (reviewer, reviewee, task)
                FOREIGN KEY (reviewee, task) REFERENCES user_task(user, task)
            )''')

    def _create_connection(self):
        db = sqlite3.connect(self.db_file)
        db.set_trace_callback(PeerReviewDB.logger.debug)
        db.execute('PRAGMA foreign_keys = 1')
        return db

