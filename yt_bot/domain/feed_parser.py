from datetime import datetime, timezone

import feedparser
from dateutil.parser import parse as parse_date

from yt_bot.models import Video


def get_rss_feed(channel_id):
    """
    Returns the RSS feed string for a given channel_id

    Arguments:
        channel_id {str} -- channel id

    Returns:
        str -- RSS feed link
    """
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def youtube_link(video_id):
    """
    Get link to a Youtube Video

    Arguments:
        video_id {str} -- video id

    Returns:
        str -- link to the youtube video
    """
    return f"https://www.youtube.com/watch?v={video_id}"


def get_video_ids_from_db(session, video_orm_class, channel_id):
    """
    Get all videos linked with a channel from the database

    Arguments:
        session {SQLAlchemy Session} -- Session to connect to the database
        video_orm_class {SQLAlchemy ORM Class} -- ORM object representing the video table
        channel_id {string} -- channel id to check for videos

    Returns:
        set -- all the unique video ids in the data base
    """
    video_ids = set()
    videos = session.query(video_orm_class).filter(
        video_orm_class.channel_id == channel_id
    )
    for video in videos:
        video_ids.add(video.video_id)
    return video_ids


def format_feed(feed):
    """
    Parses and formats the feed and returns the data that we need

    Arguments:
        feed {FeedParserDict} -- data from the feed parser

    Returns:
        list -- list of formatted data
    """
    if feed["status"] != 200:
        return
    formatted = []
    for entry in feed["entries"]:
        link = (entry.get("link") or "").lower()
        if "shorts" in link:
            continue
        f_entry = {}
        f_entry["video_id"] = entry.get("yt_videoid")
        f_entry["channel_id"] = entry.get("yt_channelid")
        f_entry["name"] = entry.get("title")
        f_entry["description"] = entry.get("summary")
        f_entry["published"] = parse_date(entry.get("published"))
        formatted.append(f_entry)

    return formatted


def filter_new_videos(feed, video_ids):
    """
    Filters the feed for videos that are not part of video_ids

    Arguments:
        feed {list} -- list of formatted feed data
        video_ids {set} -- video ids to check

    Returns:
        list|None -- feed with only new videos
    """
    if feed:
        return [video for video in feed if video["video_id"] not in video_ids]
    return


def add_videos_to_db(session, video_orm_class, feed):
    """
    Adds video data to the database

    Arguments:
        session {SQLAlchemy Session} -- Session to connect to the database
        video_orm_class {SQLAlchemy ORM Class} -- ORM object representing the video table
        feed {list} -- video data to save
    """
    session.bulk_insert_mappings(video_orm_class, feed)
    session.commit()


def fetch_new_channel_videos(session, channel_id: str) -> list[dict]:
    video_ids = get_video_ids_from_db(session, Video, channel_id)
    rss_link = get_rss_feed(channel_id)
    feed = format_feed(feedparser.parse(rss_link))
    return filter_new_videos(feed, video_ids) or []


def stamp_and_filter_feed(
    feed: list[dict],
    source_channel_id: str,
    now: datetime | None = None,
) -> list[dict]:
    if not feed:
        return []
    now = now or datetime.now(timezone.utc)
    for entry in feed:
        entry["created_at"] = now
        entry["updated_at"] = now
    return [entry for entry in feed if entry["channel_id"] == source_channel_id]
