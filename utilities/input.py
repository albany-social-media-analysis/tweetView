"""
To build master data collections, tweetView reads in specified data from a file.
File types supported: txt, csv, json
See input data template files in templates/data_templates/input/ for examples of how to structure input data

"""


from pathlib import Path
import pandas as pd

import mongo_config

class FileInputError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return self.message
        else:
            return "Unspecified FileInputError"


def read_data_from_file(data_file_path):
    data_file_path = Path(data_file_path)

    if data_file_path.is_file():

        if data_file_path.suffix == '.csv':
            master_data = pd.read_csv(data_file_path)
            return master_data

        elif data_file_path.suffix == '.json':
            try:
                master_data = pd.read_json(data_file_path, orient='records') # This expects either a single json object or a list of json objects. Corresponds to input_data_template1.json
            except ValueError:
                try:
                    master_data = pd.read_json(data_file_path, orient='records', typ='series', convert_dates=False) # This expects either a single json object or a list of json objects with only 1 key:value pair, treating the key as the index for the resulting object. Corresponds to input_data_template2.json
                except ValueError:
                    master_data = pd.read_json(data_file_path, lines=True) # This expects one json object per line. Corresponds to input_data_template3.json
            return master_data

        elif data_file_path.suffix == '.txt':
            master_data = pd.read_csv(data_file_path) # This expects a txt file with a header in the first row. Corresponds to input_data_template1.txt
            if not 'tweet_ids' in master_data.columns:
                master_data = pd.read_csv(data_file_path, names=['tweet_ids']) # This expects a txt file with no header row. Corresponds to input_data_template2.txt
            return master_data

        else:
            raise FileInputError("Unsupported file type. tweetView only supports .csv, .txt, and .json file types")

    else:
        raise FileInputError("The file path specified does not exist")

