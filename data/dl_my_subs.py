'''
Download subscriptions from my channel. Used an environment variable for this but you can change
channel_id variable to any channel
'''
from os import getenv
from dotenv import load_dotenv
from yt_bot.services import CSVService,YoutubeService

load_dotenv()

yt = YoutubeService()
channel_id = getenv('YT_CHANNEL_ID')
my_subs = yt.get_channel_subscriptions(channel_id)
CSVService.write_list_dict_to_csv(my_subs, 'my_subs.csv')
