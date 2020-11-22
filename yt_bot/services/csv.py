from yt_bot.config import logger
import csv

class CSVService:
    @staticmethod
    def write_list_dict_to_csv(list_dict, filepath):
        '''
        Saves a list of dictionaries to a CSV file

        Arguments:
            list_dict {list} -- list of dictionaries
            filepath {string} -- path to save file to
        '''
        column_names = list_dict[0].keys()
        with open(filepath, 'w') as f:
            dict_writer = csv.DictWriter(f, column_names)
            dict_writer.writeheader()
            dict_writer.writerows(list_dict)

    @staticmethod
    def read_csv_list_dict(filepath):
        '''
        Reads a CSV and creates a list of dictionaries

        Arguments:
            filepath {string} -- path to CSV to read

        Returns:
            list_dict {list} -- list of dictionaries
        '''
        list_dict = []
        try:
            with open(filepath, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    list_dict.append(row)
        except FileNotFoundError:
            logger.exception('CSV not found')
            raise

        return list_dict
