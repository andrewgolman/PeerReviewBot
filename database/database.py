import logging
import os.path
import sqlite3


class PeerReviewDB:
    logger = logging.getLogger('database')

    def __init__(self, db_file):
        self.db_file = db_file
        if not os.path.exists(db_file):
            self._create_db()
        else:
            PeerReviewDB.logger.info(
                'Found database at {}'.format(os.path.abspath(self.db_file))
            )

    def _create_db(self):
        PeerReviewDB.logger.info(
            'Creating database at {}'.format(os.path.abspath(self.db_file))
        )

        with self._create_connection() as db:
            db.execute('''
            CREATE TABLE user (
                login text PRIMARY KEY
            )''')
            db.execute('''
            CREATE TABLE task (
                name        text PRIMARY KEY,
                status      int,
                timestamp   int
            )''')
            db.execute('''
            CREATE TABLE user_task (
                id   int    PRIMARY KEY,
                user text   REFERENCES user(login),
                task text   REFERENCES task(name),
                url  text
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
        db.execute('PRAGMA foreign_keys = 1')
        return db
