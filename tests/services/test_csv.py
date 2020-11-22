import pytest
import os
from yt_bot.services import CSVService

@pytest.fixture()
def list_dict():
    return [
            {
                'name': 'Dan Aceda',
                'channel_id': 'UC924kCgLPht5dr-D8wDQk4A',
                'date_subcribed': '2016-02-27T16:47:25.000Z'
            },
            {
                'name': 'Lisa Gaitho',
                'channel_id': 'UCclpdtcfr0-hGlKjMm3cV9g',
                'date_subcribed': '2018-05-08T07:04:45.679Z'
            },
            {
                'name': "Joyce Achieng' TV",
                'channel_id': 'UC41aN7k5-dhOWH2uDM5wU8A',
                'date_subcribed': '2017-01-02T15:52:01.000Z'
            }
        ]

@pytest.fixture()
def raw_data():
    return (
        'name,channel_id,date_subcribed\n'
        'Dan Aceda,UC924kCgLPht5dr-D8wDQk4A,2016-02-27T16:47:25.000Z\n'
        'Lisa Gaitho,UCclpdtcfr0-hGlKjMm3cV9g,2018-05-08T07:04:45.679Z\n'
        'Joyce Achieng\' TV,UC41aN7k5-dhOWH2uDM5wU8A,2017-01-02T15:52:01.000Z\n'
        )

def test_write_list_dict_to_csv(tmpdir, list_dict, raw_data):
    filepath = tmpdir.join('subcriptions')
    CSVService.write_list_dict_to_csv(list_dict, filepath)
    with open(filepath, 'r') as file:
        data = file.read()
        assert data == raw_data

def test_read_csv_list_dict(tmpdir, list_dict, raw_data):
    filepath = tmpdir.join('subscriptions')
    with open(filepath, 'w') as file:
        file.write(raw_data)
    assert CSVService.read_csv_list_dict(filepath) == list_dict

def test_read_csv_list_dict_file_not_found():
    with pytest.raises(FileNotFoundError):
        CSVService.read_csv_list_dict('file/not/found')
