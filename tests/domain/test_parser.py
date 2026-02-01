from collections import namedtuple
from unittest import mock

import pytest
from dateutil.parser import parse

from yt_bot.domain.parser import (
    add_videos_to_db,
    filter_new_videos,
    format_feed,
    get_rss_feed,
    get_video_ids_from_db,
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
