from os import getenv

import tweepy

from yt_bot.config import logger
from yt_bot.domain.channel_discovery import discover_unknown_channels
from yt_bot.domain.feed_parser import (
    add_videos_to_db,
    fetch_new_channel_videos,
    stamp_and_filter_feed,
)
from yt_bot.domain.twitter import format_tweet_text, send_tweet
from yt_bot.models import Channel, UsageStat, Video
from yt_bot.services import Database, daily_rate_limit

db = Database(getenv("DB_URI"))


def tweepy_obj():
    API_KEY = getenv("TW_API_KEY")
    API_SECRET = getenv("TW_API_SECRET")
    OAUTH_TOKEN = getenv("TW_OAUTH_TOKEN")
    OAUTH_SECRET = getenv("TW_OAUTH_SECRET")
    try:
        return tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=OAUTH_TOKEN,
            access_token_secret=OAUTH_SECRET,
        )
    except tweepy.errors.TweepyException:
        logger.exception("Could not authenticate your app, check your keys")
        raise


@daily_rate_limit(max_calls=17, get_session=db.session, model=UsageStat)
def tweet_videos(twitter, feed, channel):
    """Format and tweet videos."""
    texts = format_tweet_text(feed, channel)
    for text in texts:
        try:
            send_tweet(twitter, text)
        except tweepy.errors.TweepyException as e:
            logger.error(f"Something went wrong: {e}")
            return


def run_bot():
    with db.session() as session:
        logger.info("Starting bot")
        channels = session.query(Channel).filter(Channel.category == "music")
        total = channels.count()
        twitter = tweepy_obj()

        for idx, channel in enumerate(channels, start=1):
            feed = fetch_new_channel_videos(session, channel.channel_id)
            discover_unknown_channels(session, feed, channel)
            if not feed:
                continue
            feed = stamp_and_filter_feed(feed, channel.channel_id)
            feed = sorted(feed, key=lambda entry: entry["published"])

            if feed:
                logger.info(f"{idx} of {total} | {channel.name}: {len(feed)} videos")
                add_videos_to_db(session, Video, feed)
                # Only tweet the latest video
                latest_video = feed[-1]
                tweet_videos(twitter, [latest_video], channel)

        logger.info("Finished running bot")


if __name__ == "__main__":
    run_bot()
