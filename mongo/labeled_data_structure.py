"""
This file contains a template for how labeled data will be stored in a collection called "labeled data" inside the main project db
"""

labeled_data_template = {'tweet_id': None, # the id_str corresponding to a tweet
                         'analysts_completed': {  # This is a dictionary with keys for all users assigned to the project
                             'user1': True, # 'user1' etc should be replaced by actual username for the first analyst assigned to this project
                             'user2': False # When initialized, set a user to False. When the user's label has been uploaded to Mongo, reset to True
                         },
                         'labels': {
                             'user1': {  # 'user1' should be replaced by an actual username for the first analyst assigned to this project
                                 'label1': None, # 'label1' etc should be replaced by actual label names, pulled from the data schema
                                 'label2': None
                             }
                         }}