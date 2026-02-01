from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text

from yt_bot.config import Base


class UnknownChannel(Base):
    __tablename__ = "unknown_channels"

    channel_id = Column("channel_id", String(50), primary_key=True)
    name = Column("name", String(120))
    created_at = Column("created_at", DateTime(), default=datetime.now(timezone.utc))
    updated_at = Column("updated_at", DateTime(), default=datetime.now(timezone.utc))
    deleted_at = Column("deleted_at", DateTime(), nullable=True, default=None)
