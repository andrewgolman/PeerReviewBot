#!/usr/bin/env python3

import os
import unittest as ut

from database import PeerReviewDB
from schema import TaskStatus, ReviewStatus
from schema import User, Task, UserTask, Review


class TestPeerReviewDB(ut.TestCase):

    def setUp(self):
        self._db_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'test.db'
        )
        if os.path.exists(self._db_path):
            print('Removing existing database at', self._db_path)
            os.remove(self._db_path)
        self._db = PeerReviewDB('sqlite:///' + self._db_path, echo=False)

        # define test records
        self._test_users = [
            User(login='user0'),
            User(login='user1'),
        ]

        self._test_tasks = [
            Task(name='task0'),
            Task(name='task1'),
        ]

        self._test_user_tasks = [
            UserTask(
                user=self._test_users[0],
                task=self._test_tasks[0],
                url='!',
                status=TaskStatus.WAITING_REVIEW,
                timestamp=0
            ),
            UserTask(
                user=self._test_users[0],
                task=self._test_tasks[1],
                url='@',
                status=TaskStatus.COMPLETE,
                timestamp=1
            ),
            UserTask(
                user=self._test_users[1],
                task=self._test_tasks[0],
                url='#',
                status=TaskStatus.IN_WORK,
                timestamp=0
            ),
        ]

        self._test_reviews = [
            Review(
                reviewer=self._test_users[0],
                reviewed_task=self._test_user_tasks[2],
                status=ReviewStatus.IN_WORK,
                issue_url='$'
            ),
            Review(reviewer=self._test_users[1],
                reviewed_task=self._test_user_tasks[1],
                status=ReviewStatus.CLOSED,
                issue_url='%'
            ),
        ]

        # prepopulate database
        with self._db.start_session() as db:
            for user in self._test_users:
                db.add_record(user)
            for task in self._test_tasks:
                db.add_record(task)
            for user_task in self._test_user_tasks:
                db.add_record(user_task)
            for review in self._test_reviews:
                db.add_record(review)

    def tearDown(self):
        os.remove(self._db_path)

    def test_populate(self):
        with self._db.start_session() as db:
            return
            self.assertSetEqual(
                set(db.get_all_records(User)),
                set(self._test_users)
            )
            self.assertSetEqual(
                set(db.get_all_records(Task)),
                set(self._test_tasks)
            )
            self.assertSetEqual(
                set(db.get_all_records(UserTask)),
                set(self._test_user_tasks)
            )
            self.assertSetEqual(
                set(db.get_all_records(Review)),
                set(self._test_reviews)
            )


if __name__ == '__main__':
    ut.main()

