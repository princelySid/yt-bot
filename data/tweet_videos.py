from os import getenv

import feedparser
from twython import Twython, TwythonAuthError, TwythonError

from yt_bot.config import logger
from yt_bot.domain.parser import (
    add_videos_to_db,
    filter_new_videos,
    format_feed,
    get_rss_feed,
    get_video_ids_from_db,
)
from yt_bot.domain.twitter import format_tweet_text, send_tweet
from yt_bot.models import Channel, Video
from yt_bot.services import Database

db = Database(getenv("DB_URI"))


def twython_odj():
    APP_KEY = getenv("TW_API_KEY")
    APP_SECRET = getenv("TW_API_SECRET")
    OAUTH_TOKEN = getenv("TW_OAUTH_TOKEN")
    OAUTH_SECRET = getenv("TW_OAUTH_SECRET")
    try:
        return Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_SECRET)
    except TwythonAuthError:
        logger.exception("Could not authenticate your app, check your keys")
        raise
    except TwythonError:
        logger.exception("Something went wrong")
        raise


with db.session() as session:
    logger.info("Starting bot")
    channels = session.query(Channel)
    total = channels.count()
    twitter = twython_odj()

    for idx, channel in enumerate(channels, start=1):
        channel_id = channel.channel_id
        video_ids = get_video_ids_from_db(session, Video, channel_id)
        rss_link = get_rss_feed(channel_id)
        feed = format_feed(feedparser.parse(rss_link))
        feed = filter_new_videos(feed, video_ids)
        # Next section is necessary to ensure that only videos from the channel go through
        # especially for artist channels that may also have VEVO channels
        # so this captures that
        if feed:
            channel_ids = set()
            for entry in feed:
                is_diff = entry["channel_id"] != channel_id
                is_new = entry["channel_id"] not in channel_ids
                is_in_db = (
                    session.query(Channel)
                    .filter(Channel.channel_id == entry["channel_id"])
                    .first()
                )
                if is_diff and is_new and not is_in_db:
                    channel_ids.add(entry["channel_id"])
                    _id = entry["channel_id"]
                    logger.info(f"New Channel: {_id} | {channel.name}")
            feed = [entry for entry in feed if entry["channel_id"] == channel_id]
        if feed:
            logger.info(f"{idx} of {total} | {channel.name}: {len(feed)} videos")
            texts = format_tweet_text(feed, channel)
            for text in texts:
                try:
                    send_tweet(twitter, text)
                except TwythonError:
                    logger.exception("Something went wrong")
                    raise
            add_videos_to_db(session, Video, feed)
    logger.info("Finished running bot")
