from os import getenv

import feedparser
import tweepy

from yt_bot.config import logger
from yt_bot.domain.parser import (
    add_videos_to_db,
    filter_new_videos,
    format_feed,
    get_rss_feed,
    get_video_ids_from_db,
)
from yt_bot.domain.twitter import format_tweet_text, send_tweet
from yt_bot.models import Channel, UnknownChannel, UsageStat, Video
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


def fetch_filtered_feed(session, channel_id):
    """
    Fetch RSS feed and filter to new videos not yet in DB.
    Args:
        session: SQLAlchemy session
        channel_id: YouTube channel ID

    Returns:
        List of new videos
    """
    video_ids = get_video_ids_from_db(session, Video, channel_id)
    rss_link = get_rss_feed(channel_id)
    feed = format_feed(feedparser.parse(rss_link))
    return filter_new_videos(feed, video_ids)


def discover_new_channels(session, feed, channel):
    """
    Log new channels found in feed (e.g. VEVO)
    Args:
        session: SQLAlchemy session
        feed: List of videos
        channel: Channel object
    """
    if not feed:
        return
    source_channel_id = channel.channel_id
    unknown_channel_ids = {
        entry["channel_id"]
        for entry in feed
        if entry.get("channel_id") and entry["channel_id"] != source_channel_id
    }
    if not unknown_channel_ids:
        return

    existing_channel_ids = {
        row[0]
        for row in session.query(Channel.channel_id)
        .filter(Channel.channel_id.in_(unknown_channel_ids))
        .all()
    }
    existing_unknown_ids = {
        row[0]
        for row in session.query(UnknownChannel.channel_id)
        .filter(UnknownChannel.channel_id.in_(unknown_channel_ids))
        .all()
    }
    new_channel_ids = unknown_channel_ids - existing_channel_ids - existing_unknown_ids
    if not new_channel_ids:
        return

    session.add_all(
        [
            UnknownChannel(channel_id=new_channel_id, name=channel.name)
            for new_channel_id in sorted(new_channel_ids)
        ]
    )
    session.commit()

    for new_channel_id in sorted(new_channel_ids):
        logger.info(
            f"New Channel from {channel.name}: https://www.youtube.com/channel/{new_channel_id}",
        )


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
            feed = fetch_filtered_feed(session, channel.channel_id)
            discover_new_channels(session, feed, channel)
            if not feed:
                continue
            feed = sorted(
                [entry for entry in feed if entry["channel_id"] == channel.channel_id],
                key=lambda entry: entry["published"],
            )

            if feed:
                logger.info(f"{idx} of {total} | {channel.name}: {len(feed)} videos")
                add_videos_to_db(session, Video, feed)
                # Only tweet the latest video
                latest_video = feed[-1]
                tweet_videos(twitter, [latest_video], channel)

        logger.info("Finished running bot")


if __name__ == "__main__":
    run_bot()
