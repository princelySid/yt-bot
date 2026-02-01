from datetime import datetime
from os import getenv

import feedparser

from yt_bot.config import logger
from yt_bot.domain.parser import (
    channel_video_ids,
    filter_feed,
    format_feed,
    rss_feed,
    video_db,
)
from yt_bot.models import Channel, Video
from yt_bot.services import Database

db = Database(getenv("DB_URI"))

with db.session() as session:
    channels = session.query(Channel)
    total = channels.count()
    for idx, channel in enumerate(channels, start=1):
        channel_id = channel.channel_id
        video_ids = channel_video_ids(session, Video, channel_id)
        rss_link = rss_feed(channel_id)
        feed = format_feed(feedparser.parse(rss_link))
        feed = filter_feed(feed, video_ids)
        # Next section is necessary to ensure that only videos from the channel go through
        # especially for artist channels that may also have VEVO channels
        # so this captures that
        if feed:
            channel_ids = set()
            for entry in feed:
                now = datetime.now(datetime.timezone.utc)
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
                entry["created_at"] = now
                entry["updated_at"] = now
            feed = [entry for entry in feed if entry["channel_id"] == channel_id]
            logger.info(f"{idx} of {total} | {channel.name}: {len(feed)} videos")
            video_db(session, Video, feed)
