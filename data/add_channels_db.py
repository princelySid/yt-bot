from yt_bot.models import Channel, Video
from yt_bot.services import Database
from os import getenv
from sqlalchemy_utils import create_database, database_exists
from yt_bot.config import Base
from yt_bot.services import CSVService

def create_db():
    '''
    Creates the sqlite database.
    '''
    db_path = '/absolute/path/to/database.db'
    db_uri = f'sqlite:////{db_path}'
    if database_exists(db_uri):
        return
    create_database(db_uri)

db = Database(getenv('DB_URI'))

# Uncomment this section if you've not created your database
# create_db()
# Uncomment this section if you've not created your tables
db.create_tables(Base.metadata)

uncategorised = CSVService.read_csv_list_dict('data/ke_blog.csv')
music = CSVService.read_csv_list_dict('data/ke_music.csv')

for row in uncategorised:
    row['category'] = 'uncategorised'
for row in music:
    row['category'] = 'music'

music_ids = {x['channel_id'] for x in music}
de_music = [channel for channel in uncategorised
    if channel['channel_id'] not in music_ids]
music.extend(de_music)

with db.session() as session:
        session.bulk_insert_mappings(Channel, music)
        session.commit()
