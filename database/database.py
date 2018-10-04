import logging

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from schema import TaskStatus, ReviewStatus
from schema import Base, User, Task, UserTask, Review


class PeerReviewDBSession:
    def __init__(self, session_factory):
        self._session = scoped_session(session_factory)

    def get_user(self, id=None, login=None):
        if id is not None:
            return self._session.query(User).filter(User.id == id).first()
        if login is not None:
            return self._session.query(User).filter(User.login == login).first()
        return None

    def get_task(self, name):
        return self._session.query(Task).filter(Task.name == name).first()

    def get_user_task(self, user, task):
        if user.id is None:
            user = self.get_user(user.login)
        if task.id is None:
            task = self.get_task(task.name)

        return self._session.query(UserTask).filter(
            UserTask.user_id == user.id,
            UserTask.task_id == task.id,
        ).first()

    def get_review(self, reviewer, reviewed_task):
        if reviewer.id is None:
            reviewer = self.get_user(reviewer.login)
        if reviewed_task.id is None:
            reviewed_task = self.get_user_task(reviewed_task.user, reviewed_task.task)

        return self._session.query(Review).filter(
            Review.reviewer_id      == reviewer.id,
            Review.reviewed_task_id == reviewed_task.id,
            Review.status           != ReviewStatus.CLOSED,
        ).first()

    def get_all_records(self, record_type):
        return self._session.query(record_type).all()

    def count_records(self, record_type):
        return self._session.query(record_type).count()

    def add_record(self, record):
        self._session.add(record)
        self._session.flush()

    def delete_record(self, record):
        self._session.delete(record)
        self._session.flush()

    def close(self):
        self._session.commit()
        self._session.close()


class PeerReviewDB:
    def __init__(self, db_url, echo=False):
        self._engine = create_engine(db_url, echo=echo)
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    # As proposed in
    # https://stackoverflow.com/questions/12223335
    @contextmanager
    def start_session(self):
        session = PeerReviewDBSession(self._session_factory)
        yield session
        session.close()

