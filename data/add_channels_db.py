from os import getenv

from sqlalchemy_utils import create_database, database_exists

from yt_bot.config import Base
from yt_bot.models import Channel
from yt_bot.services import Database

from data.paths import MUSIC_CSV, SUBSCRIPTIONS_CSV, UNCATEGORISED_CSV
from data.workflows import load_channels_from_csv, prepare_channel_seed_rows

db_uri = getenv("DB_URI")
if not database_exists(db_uri):
    create_database(db_uri)

db = Database(db_uri)
db.create_tables(Base.metadata)

uncategorised, music, others = load_channels_from_csv(
    str(UNCATEGORISED_CSV),
    str(MUSIC_CSV),
    str(SUBSCRIPTIONS_CSV),
)
channel_rows = prepare_channel_seed_rows(uncategorised, music, others)

with db.session() as session:
    session.bulk_insert_mappings(Channel, channel_rows)
    session.commit()
