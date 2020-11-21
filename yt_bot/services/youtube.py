from os import getenv
from dotenv import load_dotenv
from googleapiclient.discovery import build
from yt_bot.config import logger

load_dotenv()

class YoutubeService:
    @property
    def service(self):
        '''
        service {Resourse} -- A Resource object with methods for interacting with the service.
        '''
        return build(
            getenv('YT_API_SERVICE_NAME'),
            getenv('YT_API_VERSION'),
            developerKey=getenv('YT_API_KEY'))

    def get_channel_subscriptions(self, channel_id, part='snippet', **kwargs):
        '''
        Uses the YouTube data API subscriptions.list:
        https://developers.google.com/youtube/v3/docs/subscriptions
        to pull public subsriptions from a channel

        Arguments:
            channel_id {str} -- specifies a YouTube channel ID. The API will only return that
                channel's public subscriptions.

        Keyword Arguments:
            part {str} -- The part parameter specifies a comma-separated list of one or more
                subscription resource properties that the API response will include.
                (default: {'snippet'})

        Returns:
            HttpRequest -- subcription details
        '''
        subscriptions = self.service.subscriptions()
        request = subscriptions.list(
            part=part, channelId=channel_id, maxResults=50
            )
        list_channels = []
        count = 0
        while request:
            logger.info(f'Processing page {count}')
            count+=1
            results = request.execute()
            for channel in results.get('items'):
                channel_details = {}
                snippet = channel['snippet']
                channel_details['name'] = snippet['title']
                channel_details['description'] = snippet['description']
                channel_details['channel_id'] = snippet['resourceId']['channelId']
                channel_details['date_subscribed'] = snippet['publishedAt']
                list_channels.append(channel_details)
            request = subscriptions.list_next(request, results)
        logger.info(f'There are {len(list_channels)} channels')
        return list_channels
