from pymongo import MongoClient
import mongo_config

client = MongoClient(username=mongo_config.user, password=mongo_config.pwd, port=mongo_config.port)

tv_admin_db = client['TV_ADMIN']
tv_users = tv_admin_db['USERS']
# establish tool admin role for the db
client.admin.command(
    "createRole",
    "Tool Admin",
    privileges=[],
    roles=["root"]
)
# establish project lead role for the db
tv_admin_db.command(
    "createRole",
    "Project Lead",
    privileges=[
        {"resource": {"db": "TV_ADMIN", "collection": ""},
         "actions": ["createUser", "dropUser", "grantRole", "changePassword",
                     "revokeRole", "viewUser", "update", "insert"]}],
    roles=[])
# project analyst will be given read and write permissions in other dbs when they are created NOT IN
# ADMIN DB OR MAYBE JUST CREATE PROJECT ANALYST ROLES IN OTHER DBS ONLY
tv_admin_db.command(
    "createRole",
    "Project Analyst",
    privileges=[],
    roles=[])
# create a default system admin user (for dummy use and other cases)
tv_admin_db.command("CreateUser", mongo_config.tv_admin, pwd=mongo_config.tv_admin_pwd,
                    roles=[{"role": "TV_tool_admin"}])
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
