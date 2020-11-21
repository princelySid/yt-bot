from yt_bot.services import YoutubeService
from unittest import mock
from yt_bot.config import logger

channel_detials = [{
    'name':'test_title',
    'description':'test_description',
    'channel_id': 1,
    'date_subscribed':'12.30',
}]
class MockList:
    @staticmethod
    def execute():
        return {
            'items':[
                {
                    'snippet':
                    {
                        'title':'test_title',
                        'description':'test_description',
                        'publishedAt': '12.30',
                        'resourceId':{'channelId': 1}
                    }
                }
            ],
            'pageInfo':{
                'totalResults':1
            }
        }

class MockSubscription:
    @staticmethod
    def list(part, channelId, maxResults):
        return MockList()

    @staticmethod
    def list_next(request, results):
        return None

class MockService:
    @staticmethod
    def subscriptions():
        return MockSubscription()

@mock.patch('yt_bot.services.YoutubeService.service', MockService)
def test_get_playlist_items():
    yt = YoutubeService()
    result = yt.get_channel_subscriptions(1)
    assert result == channel_detials
