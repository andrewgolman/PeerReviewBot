import logging

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schema import TaskStatus, ReviewStatus
from schema import Base, User, Task, UserTask, Review


class PeerReviewDB:
    def __init__(self, db_url, echo=False):
        self._engine = create_engine(db_url, echo=echo)
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)

    @contextmanager
    def start_session(self):
        self._session = self._session_factory()
        yield self
        self._session.commit()
        self._session.close()

    def get_user(self, login):
        return self._session.query(User).filter(User.login == login).first()

    def get_task(self, name):
        return self._session.query(Task).filter(Task.name == name).first()

    def get_user_task(self, user, task):
        return self._session.query(UserTask).filter(
            UserTask.user_id == user.id,
            UserTask.task_id == task.id,
        ).first()

    def get_review(self, reviewer, user_task):
        return self._session.query(Review).filter(
            Review.reviewer_id  == reviewer.id,
            Review.user_task_id == user_task.id,
            Review.status       != ReviewStatus.CLOSED,
        ).first()

    def get_all_records(self, record_type):
        return self._session.query(record_type).all()

    def add_record(self, record):
        self._session.add(record)

    def delete_record(self, record):
        self._session.delete(record)

