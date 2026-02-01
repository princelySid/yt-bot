from sqlalchemy import Column, Integer, String

from yt_bot.config import Base


class UsageStat(Base):
    __tablename__ = "usage_stats"

    task_name = Column("task_name", String(50), primary_key=True)
    day = Column("day", String(50), index=True, unique=True)
    count = Column("count", Integer())
