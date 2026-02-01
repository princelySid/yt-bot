from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import backref, relationship

from yt_bot.config import Base


class Video(Base):
    __tablename__ = "videos"

    video_id = Column("video_id", String(20), primary_key=True)
    channel_id = Column("channel_id", String(50), ForeignKey("channels.channel_id"))
    name = Column("name", String(120))
    description = Column("description", Text())
    published = Column("published", DateTime())
    created_at = Column(
        "created_at", DateTime(), default=datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        "updated_at", DateTime(), default=datetime.now(datetime.timezone.utc)
    )

    channel = relationship("Channel", backref=backref("videos", order_by=published))
