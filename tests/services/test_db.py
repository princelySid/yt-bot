import pytest
from sqlalchemy_utils import create_database
from yt_bot.services import Database

@pytest.fixture()
def tmp_db(tmpdir):
    db_path = tmpdir.join('tmp.db')
    db_uri = f'sqlite:////{str(db_path)}'
    create_database(db_uri)
    return db_uri

def test_init(tmp_db):
    db = Database(tmp_db)
    assert db.db_uri == tmp_db

def test_init_error():
    with pytest.raises(ValueError):
        Database('sqlite:////does/not/exist')
