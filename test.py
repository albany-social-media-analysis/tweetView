import mongo_config
from admin_authentication import TVAdminAuthorizedCreationControls
from pymongo import MongoClient
from pprint import pprint

client = MongoClient(host='icehc1.arcc.albany.edu', username=mongo_config.tv_admin,
password=mongo_config.tv_admin_pwd, port=mongo_config.port, authSource=mongo_config.amdin_database)

controls = TVAdminAuthorizedCreationControls(auth_user_name=mongo_config.tv_admin,
                                          auth_password=mongo_config.tv_admin_pwd)

db = client.TV_ADMIN
#print(client.list_database_names())
#system_user_list = db.command('usersInfo')['users']
#system_user_list = [userinfo['user'] for userinfo in system_user_list]
#print(system_user_list)
#for doc in db.USERS.find():
 #   print(doc)
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
    "Scheme": 'https://docs.google.com/document/d/1nJ0rPDSKF0uhmCP3KqxpV4OxismzW0qp4XU0tpEaWuc/edit'
}})

client.testingMay19['PROJECT_INFO'].update_one({"Summary": "This is the summary of the current project you selected"},
    {'$set': {"lead": ["testUser", "testUser1"],
    "Summary": "This is the summary of the current project you selected",
    "Assigned": ['testusr', 'random user', 'random user 2'],
    "Scheme":  'https://docs.google.com/document/d/1mmiBYlAQSDOWqGdtIGyjZZcwJwZ29y00uySTRD3JDrk/edit'
}})
'''
'''
client.test_db2.command(
            "createRole",
            "Project Lead",
            privileges=[],
            roles=["dbOwner", "dbAdmin"])
client.test_db2.command(
            "createRole",
            "Project Analyst",
            privileges=[],
            roles=["readWrite"])

client.testingMay19.command(
            "createRole",
            "Project Lead",
            privileges=[],
            roles=["dbOwner", "dbAdmin"])
client.testingMay19.command(
            "createRole",
            "Project Analyst",
            privileges=[],
            roles=["readWrite"])
'''
# pprint(list(db.USERS.find({'CONTACT EMAIL': 'jqfuller@albany.edu'})))

#print(list(db.test_db2.list_collection_names()))
#print(client.test_db2['PROJECT_INFO'].find()[0]['lead'][0])
#print(client.test_db2['test_data'].find_one())
#print(db.USERS.find_one({'USER': 'TestUser20'}))
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
# db.USERS.update_one({"USER": 'SamJTest1'}, {"$set": {"USER": "samjtest1"}})
# print(db.USERS.find({"USER": 'samjtest1'})[0]['ASSIGNMENTS'])


# msg1 = controls.grant_role_to_user_in_tv_admin_db('SamJTest1', 'test_db2', 'Project Lead')
# msg2 = controls.grant_role_to_user_in_tv_admin_db('SamJTest1', 'testingMay19', 'Project Analyst')
#
# print('mgs1:' )
# print(msg1)
# print('msg2:' )
# print(msg2)
# pprint(db.command('usersInfo')['users'])
# print(db.command( "updateUser",
#                     "SamJTest1",
#                   {'user' :"samjtest1"}))
# print(client.system.command(
#     "update",
#     {"user": "SamJTest1"},
#     {'$set': {"user": "samjtest1"}}
# ))

pprint(db.command('usersInfo').find("SamJTest1"))
# for name in db.command('usersInfo')['users']:
#     if name['user'] == 'SamJTest1':
#         pprint(name)
#         print('is upper')
#     elif name['user'] == 'SamJTest1'.lower():
#         pprint(name)
#         print('is lower')
# db.command("")

# db.updateUser("SamJTest1",
#               {'user': "SamJTest1".lower()})