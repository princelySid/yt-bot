from concurrent.futures import ThreadPoolExecutor, as_completed
from os import getenv

from tqdm import tqdm

from yt_bot.config import logger
from yt_bot.domain.feed_parser import (
    add_videos_to_db,
    fetch_new_channel_videos,
    stamp_and_filter_feed,
)
from yt_bot.models import Channel, Video
from yt_bot.services import Database

MAX_WORKERS = 5  # Limit concurrent RSS fetches to avoid hammering YouTube

db = Database(getenv("DB_URI"))


def process_channel(db_instance: Database, channel_id: str, channel_name: str) -> None:
    """Process a single channel: fetch RSS, filter new videos, add to DB."""
    with db_instance.session() as session:
        feed = fetch_new_channel_videos(session, channel_id)
        if feed:
            other_channel_ids = {
                entry["channel_id"]
                for entry in feed
                if entry.get("channel_id") and entry["channel_id"] != channel_id
            }
            for new_channel_id in sorted(other_channel_ids):
                is_in_db = (
                    session.query(Channel)
                    .filter(Channel.channel_id == new_channel_id)
                    .first()
                )
                if not is_in_db:
                    logger.info(f"New Channel: {new_channel_id} | {channel_name}")
            feed = stamp_and_filter_feed(feed, channel_id)
            if feed:
                add_videos_to_db(session, Video, feed)


with db.session() as session:
    channels = [(c.channel_id, c.name) for c in session.query(Channel).all()]
    total = len(channels)

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(process_channel, db, channel_id, channel_name): (
            channel_id,
            channel_name,
        )
        for channel_id, channel_name in channels
    }
    for future in tqdm(
        as_completed(futures), total=total, desc="Adding videos to database"
    ):
        future.result()  # Raise any exception from the worker
