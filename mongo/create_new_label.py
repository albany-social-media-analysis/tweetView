from data_schema_valid import DataValidation
import mongo_config
from pymongo import MongoClient

def create_new_label():
    label = DataValidation(label_name, label_type) # First, we create the new label. This sets the label name and type,
                                                   # and it creates necessary attributes for the label
    if label.type == 'int':
        min_value = 0   # This is a placeholder. Needs to be defined by input.
        max_value = 0   # This is a placeholder. Needs to be defined by input.
        label.set_options(min_value=min_value, max_value=max_value)
    elif label.type == 'enum':
        enum_options = [] # This is a placeholder. Needs to be defined by input.
        label.set_options(options=enum_options)

    return label

def set_labels(labels=labels, project_name=project_name):
    """

    :param labels: this should be a list of label objects, where each object is one label as returned by create_new_label
    :param project_name:
    :return:
    """
    admin_client = MongoClient(authSource='TV_ADMIN', username=mongo_config.tv_admin,
                               password=mongo_config.tv_admin_pwd, port=mongo_config.port)
    project_db = admin_client[project_name]
    project_collections_info_list = project_db.command('listCollections')['cursor']['firstBatch']
    labeled_data_col_info = [collection_info for collection_info in project_collections_info_list if collection_info['name'] == 'labeledData'][0] # The list comprehension should always yield a list of len=1
    if 'validator' in labeled_data_col_info['options'].keys():
        existing_validation = labeled_data_col_info['options']['validator']['$jsonSchema']
        existing_label_scheme = existing_validation['properties']
        next_step = '' # options are 'scratch', 'edit', and 'cancel'
        if next_step == 'scratch':
            remove_validation = project_db.command({"collMod": "labeledData", "validator": {}, "validationLevel": "off"})
        elif next_step == 'edit':
            existing_labels = existing_label_scheme.keys()
            for label in labels:
                if label.name in existing_labels:
                    existing_label_details = existing_label_scheme[label_to_edit]


    else:
        existing_validation = False

    # If validation exists, prompt user to pick between deleting and starting again, adding new labels, or cancelling
    # If validation doesn't exist, just create validation

