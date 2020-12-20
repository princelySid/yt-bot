from yt_bot.config import logger

def tweet_text(feed, channel):
    ch_category = channel.category.upper()
    ch_name = channel.name
    for video in feed:
        video_name = video['name']
        video_id = video['video_id']
        text = f'[{ch_category}] New Video from {ch_name}: {video_name} '
        text_len = len(text)
        if text_len>230:
            logger.info(f'Text too long({text_len}): {text}')
            text = f'[{ch_category}] New Video from {ch_name} '
        video_link = f'https://www.youtube.com/watch?v={video_id}'
        yield text + video_link


def tweet_video(twitter, text):
    twitter.update_status(status=text)
    return None
