from pymongo import MongoClient
import mongo_config

class UserNotFound(Exception):
   def __init__(self, *args):
      if args:
         self.message = args[0]
      else:
         self.message = None

   def __str__(self):
      if self.message:
         return self.message
      else:
         return "Unspecified UserNotFound error"

class ProjectNotFound(Exception):
   def __init__(self, *args):
      if args:
         self.message = args[0]
      else:
         self.message = None

   def __str__(self):
      if self.message:
         return self.message
      else:
         return "Unspecified ProjectNotFound error"

def add_analyst_to_project(username, project_name):
    admin_client = MongoClient(authSource='TV_ADMIN', username=mongo_config.tv_admin,
                               password=mongo_config.tv_admin_pwd, port=mongo_config.port,
                               host=mongo_config.host)

    ## Confirm that user exists
    user_object = admin_client['TV_ADMIN']['USERS'].find_one({'USER': username})
    if not user_object:
        raise UserNotFound("Specified analyst user does not exist")

    ## Confirm that project exists
    system_dbs = admin_client.list_database_names()
    system_dbs = [db for db in system_dbs]
    if not project_name in system_dbs:
        raise ProjectNotFound("Specified project does not exist")

    ## Add project role to user object
    admin_client['TV_ADMIN'].command("grantRolesToUser", username, roles=[{"role": "Project Analyst", "db": project_name}])
    assign_role = "Project Analyst"

    ## Add project and role to user doc in TV_ADMIN.USERS
    current_assignments = user_object['ASSIGNMENTS']
    current_assignments.append({"PROJECT_NAME": project_name, "ROLE": "Project Analyst"})
    update_user_contact = admin_client['TV_ADMIN']['USERS'].update_one({"USER": username}, {"$set": {"ASSIGNMENTS": current_assignments}})

    return assign_role, update_user_contact
