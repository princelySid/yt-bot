from collections import namedtuple

import pytest

from yt_bot.domain.twitter import format_tweet_text, send_tweet

Channel = namedtuple("Channel", ["category", "name"])


class FakeTwitter:
    @staticmethod
    def create_tweet(text):
        return


def test_format_tweet_text():
    my_channel = Channel("Music", "princelySid")
    feed = [{"name": "Coding a YouTube Twitter Bot", "video_id": "fake_video_id"}]
    expected = (
        "[MUSIC] New Video from princelySid: Coding a YouTube Twitter Bot "
        "https://www.youtube.com/watch?v=fake_video_id"
    )
    text = list(format_tweet_text(feed, my_channel))[0]
    assert text == expected


def test_format_tweet_text_longer_than_230():
    my_channel = Channel("Music", "princelySid")
    feed = [
        {
            "name": (
                "Coding a YouTube Twitter Bot using various python libraries like feedparser, "
                "sql-alchemy and twython while also working on learning how to write tests and making "
                "long title names because I lack imagination to make this realistic"
            ),
            "video_id": "fake_video_id",
        }
    ]
    expected = "[MUSIC] New Video from princelySid https://www.youtube.com/watch?v=fake_video_id"
    text = list(format_tweet_text(feed, my_channel))[0]
    assert text == expected


def test_send_tweet():
    post = "My test tweet"
    assert send_tweet(FakeTwitter, post) == None
