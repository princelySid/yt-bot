from dateutil.parser import parse

def rss_feed(channel_id):
    '''
    Returns the RSS feed string for a given channel_id

    Arguments:
        channel_id {str} -- channel id

    Returns:
        str -- RSS feed link
    '''
    return f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'

def youtube_link(video_id):
    '''
    Get link to a Youtube Video

    Arguments:
        video_id {str} -- video id

    Returns:
        str -- link to the youtube video
    '''
    return f'https://www.youtube.com/watch?v={video_id}'

def channel_video_ids(session, video_orm_class, channel_id):
    '''
    Get all videos linked with a channel from the database

    Arguments:
        session {SQLAlchemy Session} -- Session to connect to the database
        video_orm_class {SQLAlchemy ORM Class} -- ORM object representing the video table
        channel_id {string} -- channel id to check for videos

    Returns:
        set -- all the unique video ids in the data base
    '''
    video_ids = set()
    videos =session.query(video_orm_class).filter(video_orm_class.channel_id==channel_id)
    for video in videos:
        video_ids.add(video.video_id)
    return video_ids

def format_feed(feed):
    if feed['status'] != 200:
        return
    formatted = []
    for entry in feed['entries']:
        f_entry = {}
        f_entry['video_id'] = entry.get('yt_videoid')
        f_entry['channel_id'] = entry.get('yt_channelid')
        f_entry['name'] = entry.get('title')
        f_entry['description'] = entry.get('summary')
        f_entry['published'] = parse(entry.get('published'))
        formatted.append(f_entry)

    return formatted

def filter_feed(feed, video_ids):
    if feed:
        return [video for video in feed if video['video_id'] not in video_ids]
    return

def video_db(session, video_orm_class, feed):
    session.bulk_insert_mappings(video_orm_class, feed)
    session.commit()
