from os import getenv
from dotenv import load_dotenv
from yt_bot.services import CSVService,YoutubeService

load_dotenv()

yt = YoutubeService()
my_subs = yt.get_channel_subscriptions(getenv('YT_CHANNEL_ID'))
CSVService.write_list_dict_to_csv(my_subs, 'my_subs.csv')
