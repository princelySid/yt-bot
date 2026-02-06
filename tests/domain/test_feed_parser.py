from collections import namedtuple
from datetime import datetime, timezone
from unittest import mock

import pytest
from dateutil.parser import parse

import yt_bot.domain.feed_parser as feed_parser
from yt_bot.domain.feed_parser import (
    add_videos_to_db,
    fetch_new_channel_videos,
    filter_new_videos,
    format_feed,
    get_rss_feed,
    get_video_ids_from_db,
    stamp_and_filter_feed,
    youtube_link,
)

Channel = namedtuple("Channel", ["channel_id", "video_id"])


class FakeSession:
    @staticmethod
    def query(orm_class):
        return FakeQuery()


class FakeQuery:
    @staticmethod
    def filter(channel_id):
        return [
            Channel(1, 1),
            Channel(1, 2),
            Channel(1, 3),
            Channel(1, 3),
        ]


@pytest.fixture()
def feed():
    return {
        "status": 200,
        "entries": [
            {
                "id": "yt:video:GQUMbOn7EzI",
                "guidislink": True,
                "link": "https://www.youtube.com/watch?v=GQUMbOn7EzI",
                "yt_videoid": "GQUMbOn7EzI",
                "yt_channelid": "UCaZv3iMTUibHDRyagA5h2HA",
                "title": "Muthoni Drummer Queen - Power (Official video)",
                "author": "Muthoni Drummer Queen",
                "published": "2020-03-05T07:17:35+00:00",
                "summary": "Written by Muthoni Drummer Queen",
            },
            {
                "id": "yt:video:d59aiEeDdMU",
                "guidislink": True,
                "link": "https://www.youtube.com/watch?v=d59aiEeDdMU",
                "yt_videoid": "d59aiEeDdMU",
                "yt_channelid": "UCaZv3iMTUibHDRyagA5h2HA",
                "title": "Muthoni Drummer Queen - Lover",
                "author": "Muthoni Drummer Queen",
                "published": "2018-02-13T13:01:43+00:00",
                "summary": "LOVER is the 4th Single of MDQ's upcoming album SHE",
            },
            {
                "id": "yt:video:mqSx2PLRUvs",
                "guidislink": True,
                "link": "https://www.youtube.com/watch?v=mqSx2PLRUvs",
                "yt_videoid": "mqSx2PLRUvs",
                "yt_channelid": "UCaZv3iMTUibHDRyagA5h2HA",
                "title": "Muthoni Drummer Queen - SUZIE NOMA DANCE VIDEO",
                "author": "Muthoni Drummer Queen",
                "published": "2017-11-30T10:05:50+00:00",
                "summary": "Suzie Noma is the 3rd Single of MDQ's upcoming album SHE.",
            },
        ],
    }


@pytest.fixture()
def formatted_feed():
    return [
        {
            "video_id": "GQUMbOn7EzI",
            "channel_id": "UCaZv3iMTUibHDRyagA5h2HA",
            "name": "Muthoni Drummer Queen - Power (Official video)",
            "description": "Written by Muthoni Drummer Queen",
            "published": parse("2020-03-05T07:17:35+00:00"),
        },
        {
            "video_id": "d59aiEeDdMU",
            "channel_id": "UCaZv3iMTUibHDRyagA5h2HA",
            "name": "Muthoni Drummer Queen - Lover",
            "description": "LOVER is the 4th Single of MDQ's upcoming album SHE",
            "published": parse("2018-02-13T13:01:43+00:00"),
        },
        {
            "video_id": "mqSx2PLRUvs",
            "channel_id": "UCaZv3iMTUibHDRyagA5h2HA",
            "name": "Muthoni Drummer Queen - SUZIE NOMA DANCE VIDEO",
            "description": "Suzie Noma is the 3rd Single of MDQ's upcoming album SHE.",
            "published": parse("2017-11-30T10:05:50+00:00"),
        },
    ]


def test_rss_feed():
    expected = (
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC41aN7k5-dhOWH2uDM5wU8A"
    )
    assert get_rss_feed("UC41aN7k5-dhOWH2uDM5wU8A") == expected


def test_youtube_link():
    expected = "https://www.youtube.com/watch?v=mqSx2PLRUvs"
    assert youtube_link("mqSx2PLRUvs") == expected


def test_channel_video_ids():
    expected = {1, 2, 3}
    orm_class = mock.Mock()
    assert get_video_ids_from_db(FakeSession, orm_class, 1) == expected


def test_format_feed(feed, formatted_feed):
    assert format_feed(feed) == formatted_feed


def test_format_feed_not_200():
    assert format_feed({"status": 400}) == None


def test_filter_feed(formatted_feed):
    expected = [
        {
            "video_id": "GQUMbOn7EzI",
            "channel_id": "UCaZv3iMTUibHDRyagA5h2HA",
            "name": "Muthoni Drummer Queen - Power (Official video)",
            "description": "Written by Muthoni Drummer Queen",
            "published": parse("2020-03-05T07:17:35+00:00"),
        }
    ]
    video_ids = {"d59aiEeDdMU", "mqSx2PLRUvs"}
    assert filter_new_videos(formatted_feed, video_ids) == expected


def test_video_db(formatted_feed):
    session = mock.Mock()
    add_videos_to_db(session, "orm_class", formatted_feed)
    session.bulk_insert_mappings.assert_called_with("orm_class", formatted_feed)


def test_fetch_new_channel_videos(monkeypatch):
    session = mock.Mock()
    mock_get_video_ids = mock.Mock(return_value={"old_video"})
    mock_get_rss = mock.Mock(return_value="rss://channel/feed")
    mock_parse = mock.Mock(return_value={"status": 200, "entries": []})
    mock_format = mock.Mock(
        return_value=[
            {"video_id": "old_video", "channel_id": "channel-1"},
            {"video_id": "new_video", "channel_id": "channel-1"},
        ]
    )
    mock_filter = mock.Mock(
        return_value=[{"video_id": "new_video", "channel_id": "channel-1"}]
    )

    monkeypatch.setattr(feed_parser, "get_video_ids_from_db", mock_get_video_ids)
    monkeypatch.setattr(feed_parser, "get_rss_feed", mock_get_rss)
    monkeypatch.setattr(feed_parser.feedparser, "parse", mock_parse)
    monkeypatch.setattr(feed_parser, "format_feed", mock_format)
    monkeypatch.setattr(feed_parser, "filter_new_videos", mock_filter)

    result = fetch_new_channel_videos(session, "channel-1")

    assert result == [{"video_id": "new_video", "channel_id": "channel-1"}]
    mock_get_video_ids.assert_called_once_with(session, feed_parser.Video, "channel-1")
    mock_get_rss.assert_called_once_with("channel-1")
    mock_parse.assert_called_once_with("rss://channel/feed")
    mock_format.assert_called_once()
    mock_filter.assert_called_once_with(mock_format.return_value, {"old_video"})


def test_fetch_new_channel_videos_returns_empty_list_when_none(monkeypatch):
    monkeypatch.setattr(feed_parser, "get_video_ids_from_db", mock.Mock(return_value=set()))
    monkeypatch.setattr(feed_parser, "get_rss_feed", mock.Mock(return_value="rss://empty"))
    monkeypatch.setattr(feed_parser.feedparser, "parse", mock.Mock(return_value={}))
    monkeypatch.setattr(feed_parser, "format_feed", mock.Mock(return_value=[]))
    monkeypatch.setattr(feed_parser, "filter_new_videos", mock.Mock(return_value=None))

    assert fetch_new_channel_videos(mock.Mock(), "channel-2") == []


def test_stamp_and_filter_feed():
    now = datetime(2026, 2, 6, tzinfo=timezone.utc)
    feed = [
        {"video_id": "a", "channel_id": "chan-1"},
        {"video_id": "b", "channel_id": "chan-2"},
    ]

    result = stamp_and_filter_feed(feed, "chan-1", now=now)

    assert result == [
        {
            "video_id": "a",
            "channel_id": "chan-1",
            "created_at": now,
            "updated_at": now,
        }
    ]
    assert feed[1]["created_at"] == now
    assert feed[1]["updated_at"] == now


def test_stamp_and_filter_feed_empty_feed():
    assert stamp_and_filter_feed([], "chan-1") == []
