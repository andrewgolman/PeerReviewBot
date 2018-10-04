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
            os.remove(self._db_path)
        self._db = PeerReviewDB('sqlite:///' + self._db_path, echo=False)

        # define test records
        self._test_users = [
            User(id=0, login='user0'),
            User(id=1, login='user1'),
            User(id=2, login='user2'),
        ]

        self._test_tasks = [
            Task(name='task0'),
            Task(name='task1'),
            Task(name='task2'),
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
            UserTask(
                user=self._test_users[2],
                task=self._test_tasks[2],
                url='^',
                status=TaskStatus.COMPLETE,
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
            Review(
                reviewer=self._test_users[1],
                reviewed_task=self._test_user_tasks[1],
                status=ReviewStatus.CLOSED,
                issue_url='%'
            ),
        ]

    def tearDown(self):
        os.remove(self._db_path)
        pass

    def test_repr(self):
        self.assertEqual(
            repr(self._test_tasks[0]),
            '<Task: id={}, name={}>'.format(
                self._test_tasks[0].id,
                self._test_tasks[0].name
            )
        )

    def test_hash_and_eq(self):
        user0 = self._test_users[0]
        identical_user = User(id=user0.id, login=user0.login)

        self.assertIsNot(user0, identical_user)
        self.assertEqual(user0, identical_user)
        self.assertEqual(hash(user0), hash(identical_user))

    def test_persistence(self):
        with self._db.start_session() as session:
            self.assertIsNone(self._test_tasks[0].id)
            session.add_record(self._test_tasks[0])
            self.assertIsNotNone(self._test_tasks[0].id)

        with self._db.start_session() as session:
            self.assertIsNotNone(session.get_task(self._test_tasks[0].name))

    def test_add(self):
        with self._db.start_session() as session:
            self._prepopulate_db(session)
            self._assert_population_equals(
                session,
                self._test_users, 
                self._test_tasks,
                self._test_user_tasks,
                self._test_reviews
            )

    def test_delete(self):
        with self._db.start_session() as session:
            self._prepopulate_db(session)

            session.delete_record(self._test_reviews[-1])
            session.delete_record(self._test_user_tasks[-1])
            session.delete_record(self._test_tasks[-1])
            session.delete_record(self._test_users[-1])

            self._assert_population_equals(
                session,
                self._test_users[:-1],
                self._test_tasks[:-1],
                self._test_user_tasks[:-1],
                self._test_reviews[:-1]
            )

    def _assert_population_equals(self, session, users, tasks, user_tasks, reviews):
        records_types = [
            (users, User),
            (tasks, Task),
            (user_tasks, UserTask),
            (reviews, Review)
        ]

        for records, records_type in records_types:
            self.assertSetEqual(
                frozenset(records),
                frozenset(session.get_all_records(records_type))
            )

    def _prepopulate_db(self, session):
        records_list = [
            self._test_users,
            self._test_tasks,
            self._test_user_tasks,
            self._test_reviews
        ]

        for records in records_list:
            for record in records:
                session.add_record(record)


if __name__ == '__main__':
    ut.main()

