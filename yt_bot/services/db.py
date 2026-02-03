from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import select
from sqlalchemy_utils import database_exists

from yt_bot.config import logger


class Database:
    def __init__(self, db_uri):
        if database_exists(db_uri):
            self.db_uri = db_uri
        else:
            raise ValueError(f"Database does not exist: {db_uri}")

    @property
    def engine(self):
        return create_engine(self.db_uri)

    def create_tables(self, metadata):
        metadata.create_all(self.engine)

    @contextmanager
    def session(self):
        session_maker = sessionmaker(bind=self.engine)
        session = scoped_session(session_maker)
        try:
            yield session
        except Exception:
            logger.exception("Really should not catch all excepitions like this")
            raise
        finally:
            session.remove()
