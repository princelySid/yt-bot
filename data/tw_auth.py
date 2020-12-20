from twython import Twython, TwythonAuthError, TwythonError
from os import getenv
from dotenv import load_dotenv
from yt_bot.config import logger
load_dotenv()

APP_KEY = getenv('TW_API_KEY')
APP_SECRET = getenv('TW_API_SECRET')
try:
    twitter = Twython(APP_KEY, APP_SECRET)
except TwythonAuthError:
    logger.exception('Could not authenticate your app, check your keys')
    raise
auth = twitter.get_authentication_tokens()
o_token = auth['oauth_token']
ot_secret = auth['oauth_token_secret']
print(auth['auth_url'])
oauth_verifier = input('Please open the URL above and enter the PIN code here: ')
try:
    tw = Twython(APP_KEY, APP_SECRET, o_token, ot_secret)
    oauth = tw.get_authorized_tokens(oauth_verifier)
except TwythonError:
    logger.exception('Something went wrong, possibly the PIN is expired/invalid')
    raise
token = oauth['oauth_token']
secret = oauth['oauth_token_secret']
print('\nAdd these to the .env file:')
print(f'TW_OAUTH_TOKEN= {token}')
print(f'TW_OAUTH_SECRET= {secret}')
