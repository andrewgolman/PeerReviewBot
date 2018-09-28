import enum

from sqlalchemy import Column
from sqlalchemy import Enum, Integer, String, Time
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base


class TaskStatus(enum.Enum):
    WAITING_REVIEW  = 1
    IN_PROGESS      = 2
    COMPLETE        = 3


class ReviewStatus(enum.Enum):
    WAITING_REVIEWER    = 1
    IN_PROGRESS         = 2
    CLOSED              = 3


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id      = Column(Integer, primary_key=True)
    login   = Column(String(40))


class Task(Base):
    __tablename__ = 'task'

    id      = Column(Integer, primary_key=True)
    name    = Column(String(100), nullable=False)


class UserTask(Base):
    __tablename__ = 'user_tasks'

    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey('user.id'), nullable=False)
    task_id     = Column(Integer, ForeignKey('task.id'), nullable=False)
    url         = Column(String(200), nullable=False)
    status      = Column(Enum(TaskStatus), default=TaskStatus.WAITING_REVIEW, nullable=False)
    timestamp   = Column(Time, nullable=False)


class Review(Base):
    __tablename__ = 'review'

    id          = Column(Integer, primary_key=True)
    reviewer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    task_id     = Column(Integer, ForeignKey('user_task.id'), nullable=False)
    status      = Column(Time, nullable=False)

