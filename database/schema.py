import enum

from sqlalchemy import Column
from sqlalchemy import BigInteger, Enum, Integer, String
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


class TaskStatus(enum.Enum):
    WAITING_REVIEW  = 1
    IN_WORK         = 2
    COMPLETE        = 3


class ReviewStatus(enum.Enum):
    WAITING_REVIEWER    = 1
    IN_WORK             = 2
    CLOSED              = 3


Base = declarative_base()

def _base_get_columns_dict(self):
    columns_dict = {}
    for column in self.__table__.columns:
        columns_dict[column.name] = getattr(self, column.name)
    return columns_dict

def _base_get_columns_frozenset(self):
    return frozenset(self._get_columns_dict().items())

def _base_repr(self):
    columns = []
    for column, value in sorted(self._get_columns_dict().items()):
        columns.append('{}={}'.format(column, value))
    return '<{}: {}>'.format(self.__class__.__name__, ', '.join(columns))

def _base_hash(self):
    return hash(self._get_columns_frozenset())

def _base_eq(self, other):
    return self._get_columns_frozenset() == other._get_columns_frozenset()

Base._get_columns_dict = _base_get_columns_dict
Base._get_columns_frozenset = _base_get_columns_frozenset
Base.__repr__ = _base_repr
Base.__hash__ = _base_hash
Base.__eq__ = _base_eq


class User(Base):
    __tablename__ = 'user'

    id      = Column(Integer, primary_key=True)
    login   = Column(String(40))
    UniqueConstraint(login)



class Task(Base):
    __tablename__ = 'task'

    id      = Column(Integer, primary_key=True, autoincrement=True)
    name    = Column(String(100), nullable=False)

    UniqueConstraint(name)


class UserTask(Base):
    __tablename__ = 'user_tasks'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey('user.id'), nullable=False)
    task_id     = Column(Integer, ForeignKey('task.id'), nullable=False)
    url         = Column(String(200), nullable=False)
    status      = Column(Enum(TaskStatus), default=TaskStatus.WAITING_REVIEW, nullable=False)
    timestamp   = Column(BigInteger, nullable=False)

    UniqueConstraint(user_id, task_id)

    user = relationship(User, back_populates='tasks')
    task = relationship(Task, back_populates='attempts')


User.tasks    = relationship(UserTask, order_by=UserTask.id, back_populates='user')
Task.attempts = relationship(UserTask, order_by=UserTask.id, back_populates='task')


class Review(Base):
    __tablename__ = 'review'

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_id         = Column(Integer, ForeignKey('user.id'), nullable=False)
    reviewed_task_id    = Column(Integer, ForeignKey('user_tasks.id'), nullable=False)
    status              = Column(Enum(ReviewStatus), nullable=False)
    issue_url           = Column(String(200))

    UniqueConstraint(issue_url)

    reviewer        = relationship(User, back_populates='outgoing_reviews')
    reviewed_task   = relationship(UserTask, back_populates='reviews')


User.outgoing_reviews = relationship(Review, order_by=Review.id, back_populates='reviewer')
UserTask.reviews      = relationship(Review, order_by=Review.id, back_populates='reviewed_task')

