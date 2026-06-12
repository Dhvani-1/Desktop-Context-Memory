from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Memory(Base):

    __tablename__ = "memories"

    id = Column(Integer, primary_key=True)

    createdAt = Column(String)

    sourceApp = Column(String)

    windowTitle = Column(String)

    rawContext = Column(String)

    summary = Column(String)

    type = Column(String)

    intent = Column(String)

    topic = Column(String)

    tags = Column(String)

    sensitivity = Column(String)

    usefulnessScore = Column(Float)

    suggestedNextAction = Column(String)

    screenshot = Column(String)

    pending_confirmation = Column(Integer, default=0, nullable=True)

    sensitivityReason = Column(String, nullable=True)

    title = Column(String, nullable=True)

    isImportant = Column(Boolean, default=False, nullable=True)

    sessionId = Column(String, nullable=True)

    sessionStart = Column(String, nullable=True)

    sessionEnd = Column(String, nullable=True)


class WorkSession(Base):

    __tablename__ = "work_sessions"

    sessionId = Column(String, primary_key=True)

    summary = Column(String, nullable=True)