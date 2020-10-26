import mongo_config
import admin_authentication
from pymongo import MongoClient

client = MongoClient(host='icehc1.arcc.albany.edu', username=mongo_config.tv_admin,
password=mongo_config.tv_admin_pwd, port=mongo_config.port, authSource=mongo_config.amdin_database)

db = client.TV_ADMIN
#print(client.list_database_names())
#system_user_list = db.command('usersInfo')['users']
#system_user_list = [userinfo['user'] for userinfo in system_user_list]
#print(system_user_list)
for doc in db.USERS.find():
    print(doc)
#print(db.USERS.find_one({"USER": "TV_default_admin"}))
'''
db.USERS.update_one({"USER": "testusr"},
                {"$set": {"ASSIGNMENTS":
                         [{"ROLE": "Project Lead",
                         "PROJECT_NAME": "test_db2"},
                         {"ROLE": "Project Analyst",
                         "PROJECT_NAME": "testingMay19"}]}})
print(db.USERS.find({"USER": "testusr"})[0])'''

#db.USERS.update_one({"USER": None},{"$set": {"USER": "testusr"}})
#print(db.USERS.find({"USER": None})[0]['ASSIGNMENTS'])
#print(client.list_database_names())
'''
client.test_db2['PROJECT_INFO'].update_one({"Summary": "This is the summary of the current project you selected"},
    {'$set': {"lead": ["testusr"],
    "Summary": "This is the summary of the current project you selected",
    "Assigned": ['random user', 'random user 2'],
    "Scheme": {
        'dataset 1': 'https://docs.google.com/document/d/1nJ0rPDSKF0uhmCP3KqxpV4OxismzW0qp4XU0tpEaWuc/edit',
        'dataset 2': None,
        'dataset 3': None
        }
}})

client.testingMay19['PROJECT_INFO'].update_one({"Summary": "This is the summary of the current project you selected"},
    {'$set': {"lead": ["testUser", "testUser1"],
    "Summary": "This is the summary of the current project you selected",
    "Assigned": ['testusr', 'random user', 'random user 2'],
    "Scheme": {
        'dataset 1': 'https://docs.google.com/document/d/1mmiBYlAQSDOWqGdtIGyjZZcwJwZ29y00uySTRD3JDrk/edit',
        'dataset 2': None,
        'dataset 3': None
        }
}})
'''

#print(list(db.test_db2.list_collection_names()))
#print(client.test_db2['PROJECT_INFO'].find()[0]['lead'][0])
#print(client.test_db2['test_data'].find_one())
