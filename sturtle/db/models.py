from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.functions import now
from sqlalchemy.sql.sqltypes import PickleType, DateTime
from uuid import uuid4

from sturtle.db import Base


def generate_uuid():
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String)

    def __repr__(self):
        return f"<User(name={self.name})>"


class Thread(Base):
    __tablename__ = "threads"

    id = Column(String, primary_key=True, index=True)
    survey_id = Column(String)
    user_id = Column(String)

    def __repr__(self):
        return f"<Thread(name={self.name}, survey_id={self.survey_id}, answers={self.answers})>"


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String)
    description = Column(String)
    prompt = Column(String)
    created_at = Column(DateTime, default=now())

    def __repr__(self):
        return f"<Survey(name={self.name}, prompt={self.prompt})>"


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    data = Column(PickleType)
