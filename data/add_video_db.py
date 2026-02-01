from datetime import datetime
from os import getenv

import feedparser

from yt_bot.config import logger
from yt_bot.domain.parser import (
    add_videos_to_db,
    filter_new_videos,
    format_feed,
    get_rss_feed,
    get_video_ids_from_db,
)
from yt_bot.models import Channel, Video
from yt_bot.services import Database

db = Database(getenv("DB_URI"))

with db.session() as session:
    channels = session.query(Channel)
    total = channels.count()
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
            add_videos_to_db(session, Video, feed)
