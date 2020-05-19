from pymongo import MongoClient
from pymongo import errors as pymongo_errors
import mongo_config

client = MongoClient(username=mongo_config.user, password=mongo_config.pwd, port=mongo_config.port) # for this script, mongo_config.user must be an existing root user in Mongo

tv_admin_db = client['TV_ADMIN']
tv_users = tv_admin_db['USERS']
# establish tool admin role for the db
try:
    client.admin.command("createRole","Tool Admin",privileges=[],roles=["root"])
except pymongo_errors.OperationFailure:
    print("Tool Admin role already exists. Moving on.")
    pass

# establish project lead role for the db
try:
    tv_admin_db.command("createRole","Project Lead",privileges=[
            {"resource": {"db": "TV_ADMIN", "collection": ""},
             "actions": ["createUser", "dropUser", "grantRole", "changePassword",
                         "revokeRole", "viewUser", "update", "insert"]}],
        roles=[])
except pymongo_errors.OperationFailure:
    print("Project Lead role already exists. Moving on.")
    pass

# project analyst will be given read and write permissions in other dbs when they are created NOT IN
# ADMIN DB OR MAYBE JUST CREATE PROJECT ANALYST ROLES IN OTHER DBS ONLY
try:
    tv_admin_db.command("createRole","Project Analyst",privileges=[],roles=[])
except pymongo_errors.OperationFailure:
    print("Project Analyst role already exists. Moving on.")
    pass

# create a default system admin user (for dummy use and other cases)
try:
    tv_admin_db.command("createUser", mongo_config.tv_admin, pwd=mongo_config.tv_admin_pwd,
                        roles=[{"role": "TV_tool_admin", "db": "admin"}])
    # create and insert document into user collection for the default user
    # the assignments field will be an array object that list a project and
    # role that a user has for each project they are assigned to
    default_doc = {
        "FIRST NAME": "TV_default_admin",
        "LAST NAME": "TV_default_admin",
        "USER": "TV_default_admin",
        "CONTACT EMAIL": "TV_default_admin",
        "ASSIGNMENTS": [{"PROJECT_NAME": "ALL", "ROLE": "TOOL ADMIN"}]
    }
    tv_users.insert_one(default_doc)
except pymongo_errors.OperationFailure:
    print("Tool Admin user already exists. Moving on.")
    pass
