import os

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship, Session

_Base = declarative_base()
_Engine = create_engine(str(os.getenv('DATABASE_CONNECTION')), echo=True, future=True)


def create_session() -> Session:
    return Session(_Engine)


class Bot(_Base):
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)


class Admin(_Base):
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)


class User(_Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    display_name = Column(Text, nullable=False)
    google_id = Column(String(255), nullable=True, unique=True)
    is_bot = Column(Boolean, unique=False, nullable=False, default=False)
    is_admin = Column(Boolean, unique=False, nullable=False, default=False)

    submissions = relationship("Submission", back_populates="user_id")

    def __repr__(self):
        return f"User(id={self.id!r}, display_name={self.display_name!r})"


class Submission:
    __tablename__ = 'submission'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    submission_date = Column(DateTime, unique=False, nullable=False)
    url = Column(Text, unique=False, nullable=False)
    active = Column(Boolean, unique=False, nullable=False, default=True)
    files_hash = Column(Text, unique=False, nullable=False)

    user = relationship("User", back_populates="submissions")
    results = relationship("Result", back_populates="submission_id")


class Match:
    __tablename__ = 'match'

    id = Column(Integer, primary_key=True)
    match_date = Column(DateTime, unique=False, nullable=False)
    recording = Column(Text, unique=False, nullable=False)

    results = relationship("Result", back_populates="match_id")


class Result:
    __tablename__ = 'result'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('match.id'), nullable=False)
    submission_id = Column(Integer, ForeignKey('submission.id'), nullable=False)
    outcome = Column(Integer, unique=False, nullable=False)
    milli_points_delta = Column(Integer, unique=False, nullable=False)
    healthy = Column(Boolean, unique=False, nullable=False)
    player_id = Column(Text, unique=False, nullable=False)

    submission = relationship("Submission", back_populates="results")
    match = relationship("Match", back_populates="results")


def create_tables():
    _Base.metadata.create_all(_Engine)
