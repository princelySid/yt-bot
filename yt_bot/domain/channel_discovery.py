from yt_bot.config import logger
from yt_bot.models import Channel, UnknownChannel


def discover_unknown_channels(session, feed: list[dict], source_channel) -> set[str]:
    if not feed:
        return set()
    source_channel_id = source_channel.channel_id
    unknown_channel_ids = {
        entry["channel_id"]
        for entry in feed
        if entry.get("channel_id") and entry["channel_id"] != source_channel_id
    }
    if not unknown_channel_ids:
        return set()

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
        return set()

    session.add_all(
        [
            UnknownChannel(channel_id=channel_id, name=source_channel.name)
            for channel_id in sorted(new_channel_ids)
        ]
    )
    session.commit()

    for channel_id in sorted(new_channel_ids):
        logger.info(
            f"New Channel from {source_channel.name}: "
            f"https://www.youtube.com/channel/{channel_id}"
        )
    return new_channel_ids

