from sqlalchemy import Column, String, Text
from yt_bot.config import Base

class Channel(Base):
    __tablename__ = 'channels'

    channel_id = Column('channel_id', String(50), primary_key=True)
    name = Column('name', String(120))
    description = Column('description', Text())
    category = Column('category', String(20), index=True, nullable=False)
