from pymongo import MongoClient
from pathlib import Path
import mongo_config


def input_data_to_master_data(db_login, user_name_login, pwd_login, project_name, data_file_path):
    authorized_client = MongoClient(db_login, username=user_name_login, password=pwd_login, path=mongo_config.path)

    # check if project has been initialized
    system_dbs = authorized_client.list_database_names()
    system_dbs = [db['name'] for db in system_dbs]

    if project_name in system_dbs:

        # file assessment
        data_file_path = Path(data_file_path)
        if data_file_path.exists():

            if data_file_path.is_file():

                if data_file_path.suffix == '.csv':
                    with open(data_file_path, 'r') as csv_file:
                        from csv import DictReader
                        dataset_reader = DictReader(csv_file)
                        master_data = [dict(row) for row in dataset_reader]
                    md_collection = [authorized_client[project_name]['MASTER'].insert_one(doc) for doc in master_data]
                    approved_message = data_file_path.name, "has been successfully uploaded as the project's master " \
                                                            "dataset"
                    return approved_message

                elif data_file_path.suffix == '.json':
                    import pandas as pd
                    try:
                        json_file = pd.read_json(data_file_path, orient='records')
                    except ValueError:
                        json_file = pd.read_json(data_file_path, lines=True)
                    rows = json_file.iterrows()
                    master_data = [dict(row.__next__()[1]) for row in rows]
                    md_collection = [authorized_client[project_name]['MASTER'].insert_one(doc) for doc in master_data]
                    approved_message = data_file_path.name, "has been successfully uploaded as the project's master" \
                                                            " dataset"
                    return approved_message

                elif data_file_path.suffix == '.txt':
                    import pandas as pd
                    txt_file = pd.read_fwf(data_file_path)
                    rows = txt_file.iterrows()
                    master_data = [dict(row.__next_()[1]) for row in rows]
                    md_collection = [authorized_client[project_name]['MASTER'].insert_one(doc) for doc in master_data]
                    approved_message = data_file_path.name, "has been successfully uploaded as the project's master" \
                                                            " dataset"
                    return approved_message

                else:
                    denied_message = "Unsupported file type. Tweet view only supports .csv, .txt, and .json file types"
                    return denied_message

            else:
                denied_message = "This is not a valid file path"
                return denied_message

        else:
            denied_message = "The file path specified does not exist"
            return denied_message

    else:

        denied_message = "The project name you entered does not exist"
        return denied_message
