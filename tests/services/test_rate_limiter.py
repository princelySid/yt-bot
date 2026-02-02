from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from yt_bot.config import Base
from yt_bot.models.usage_stat import UsageStat
from yt_bot.services.rate_limiter import daily_rate_limit


@pytest.fixture
def db_session(tmp_path):
    """Create an in-memory SQLite database with UsageStat table."""
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def limited_func(db_session):
    """A function decorated with daily_rate_limit(max_calls=2)."""

    @daily_rate_limit(max_calls=2, session=db_session, model=UsageStat)
    def my_task():
        return "done"

    return my_task


def test_allows_calls_under_limit(limited_func):
    """Function executes when under the rate limit."""
    assert limited_func() == "done"
    assert limited_func() == "done"


def test_raises_when_limit_exceeded(limited_func):
    """Raises Exception when max_calls is exceeded."""
    limited_func()
    limited_func()
    with pytest.raises(Exception, match="Rate limit exceeded for my_task"):
        limited_func()


def test_tracks_usage_in_database(limited_func, db_session):
    """Usage count is persisted in the database."""
    limited_func()
    limited_func()

    today = date.today().strftime("%Y-%m-%d")
    usage_stat = (
        db_session.query(UsageStat)
        .filter(UsageStat.task_name == "my_task", UsageStat.day == today)
        .first()
    )
    assert usage_stat is not None
    assert usage_stat.count == 2


def test_uses_today_for_tracking(db_session):
    """Rate limit tracks usage by task name and current date."""

    @daily_rate_limit(max_calls=1, session=db_session, model=UsageStat)
    def daily_task():
        return "ok"

    with patch("yt_bot.services.rate_limiter.date") as mock_date:
        mock_date.today.return_value = MagicMock()
        mock_date.today.return_value.strftime.return_value = "2025-02-01"
        assert daily_task() == "ok"
        with pytest.raises(Exception, match="Rate limit exceeded for daily_task"):
            daily_task()


def test_preserves_function_metadata(db_session):
    """Decorator preserves the wrapped function's name and docstring."""

    @daily_rate_limit(max_calls=10, session=db_session, model=UsageStat)
    def documented_task():
        """A well-documented task."""
        return 42

    assert documented_task.__name__ == "documented_task"
    assert documented_task.__doc__ == "A well-documented task."
    assert documented_task() == 42
