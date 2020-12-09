from os import getenv
from sqlalchemy_utils import create_database, database_exists
from yt_bot.config import Base
from yt_bot.models import Channel, Video
from yt_bot.services import CSVService, Database

db_uri = getenv('DB_URI')
if not database_exists(db_uri):
    create_database(db_uri)

db = Database(db_uri)
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
