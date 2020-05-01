# this file use case if for authentication and project(db) initialization
# by users who the permission to do so on the admin db

from pymongo import MongoClient
import mongo_config


class TVAdminAuthorizedCreationControls:

    def __init__(self, auth_user_name, auth_password):
        self.auth_user_name = auth_user_name
        self.auth_password = auth_password
        self.client = MongoClient(authSource='TV_ADMIN', username=self.auth_user_name, password=self.auth_password,
                                  port=mongo_config.port)
        self.tv_admin_db = self.client.TV_ADMIN
        system_user_list = self.tv_admin_db.command('userInfo')['users']
        system_user_list = [userinfo['user'] for userinfo in system_user_list]

    def create_tool_admin(self, user_name, pwd, email, first_name=None, last_name=None):

        if user_name in system_user_list:
            denied_message = 'This user name is  already in use'
            return denied_message, None, None, None
        else:
            self.tv_admin_db.command("createUser", user_name, pwd=pwd, roles=[{'role': 'Tool Admin', 'db': 'TV_ADMIN'}])
            new_user_contact_doc = {"FIRST NAME": first_name,
                                    "LAST NAME": last_name,
                                    "USER": user_name,
                                    "CONTACT EMAIL": email,
                                    "ASSIGNMENTS": [{"PROJECT_NAME": "ALL", "ROLE": "TOOL ADMIN"}]
                                    }
            self.tv_admin_db.USERS.insert_one(new_user_contact_doc)

            approved_message = "Tool admin ", user_name, " created"
            approved_message_2 = "New user's information has been uploaded to USER collection in ADMIN Database:"
            return approved_message, approved_message_2, new_user_contact_doc, None

    def create_project_lead(self, user_name, pwd, email, first_name=None, last_name=None, db_accesses=[]):
        if len(db_accesses) > 0:
            if user_name in system_user_list:
                denied_message = 'This user name already in use'
                return denied_message, None, None, None
            else:
                all_roles_for_dbs = [{"role": "Project Lead", "$db": db_access} for db_access in db_accesses]
                all_assignments = [{"PROJECT_NAME": db, "ROLE": "Project Lead"} for db in db_accesses]
                self.tv_admin_db.command("createUser", user_name, pwd=pwd,
                                       roles=all_roles_for_dbs.insert(0, {"role": "Project Lead", "db": "TV_ADMIN"}))
                new_user_contact_doc = {
                    "FIRST NAME": first_name,
                    "LAST NAME": last_name,
                    "USER": user_name,
                    "CONTACT EMAIL": email,
                    "ASSIGNMENTS": all_assignments
                }
                self.tv_admin_db.USER.insert_one(new_user_contact_doc)
                approved_message_1 = "project lead", user_name, "created in: "
                approved_message_2 = ""
                for permitted_db in all_roles_for_dbs:
                    approved_message_2 += permitted_db+'\n'
                approved_message_3 = "New user's information has been uploaded to USER collection in ADMIN Database:"
                return approved_message_1, approved_message_2, approved_message_3, new_user_contact_doc
        else:
            if user_name in system_user_list:
                denied_message = 'This user name already in use'
                return denied_message, None, None, None
            else:
                self.tv_admin_db.command("createUser", user_name, pwd=pwd,
                                         roles=[{"role": "Project Lead", "db": "TV_ADMIN"}])
                new_user_contact_doc = {
                    "FIRST NAME": first_name,
                    "LAST NAME": last_name,
                    "USER": user_name,
                    "CONTACT EMAIL": email,
                    "ASSIGNMENTS": [],
                }
                self.tv_admin_db.USERS.insert_one(new_user_contact_doc)
                approved_message = "project lead ", user_name, " created in TV_ADMIN Database"
                approved_message_2 = "New user's information has been uploaded to USER collection in ADMIN Database:"
                return approved_message, approved_message_2, new_user_contact_doc, None

    def create_project_analyst(self, user_name, pwd, email, first_name=None, last_name=None, db_accesses=[]):
        if len(db_accesses) > 0:
            if user_name in system_user_list:
                denied_message = 'This user name is already in use'
                return denied_message, None, None, None
            else:
                all_roles_for_dbs = [{"role": "Project Analyst", "$db": db_access} for db_access in db_accesses]
                all_assignments = [{"PROJECT NAME": db, "ROLE": "Project Analyst"} for db in db_accesses]
                self.tv_admin_db.command("createUser", user_name, pwd=pwd,
                           roles=all_roles_for_dbs.insert(0, {"role": "Project Analyst", "db": "TV_ADMIN"}))
                new_user_contact_doc = {
                    "FIRST NAME": first_name,
                    "LAST NAME": last_name,
                    "USER": user_name,
                    "CONTACT EMAIL": email,
                    "ASSIGNMENTS": all_assignments,
                }
                self.tv_admin_db.USERS.insert_one(new_user_contact_doc)
                approved_message_1 = "project analyst", user_name, "created in: "
                approved_message_2 = ""
                for permitted_db in all_roles_for_dbs:
                    approved_message_2 += permitted_db + '\n'
                approved_message_3 = "New user's information has been uploaded to USER collection in ADMIN Database:"
                return approved_message_1, approved_message_2, approved_message_3, new_user_contact_doc
        else:
            if user_name in system_user_list:
                denied_message = 'This user name is already in use'
                return denied_message, None, None, None
            else:
                self.tv_admin_db.command("createUser", user_name, pwd=pwd,
                                         roles=[{"role": "Project Analyst", "db": "TV_ADMIN"}])
                new_user_contact_doc = {
                    "FIRST NAME": first_name,
                    "LAST NAME": last_name,
                    "USER": user_name,
                    "CONTACT EMAIL": email,
                    "ASSIGNMENTS": [],
                }
                self.tv_admin_db.USERS.insert_one(new_user_contact_doc)
                approved_message = "project analyst ", user_name, " created in TV_ADMIN Database"
                approved_message_2 = "New user's information has been uploaded to USER collection in ADMIN Database:"
                return approved_message, approved_message_2, new_user_contact_doc, None

    # This method will be automatically done when a user creates a new project
    # this method is mainly for when a user needs to gain additional access to a new
    # project but did not initially start in the new db
    # projects leads assignment field in the contact doc will automatically be updated
    def grant_role_to_user_in_tv_admin_db(self, user_name, project_db_name, new_role):
        # check db if user exist in admin db as a user
        if user_name in system_user_list:
            user_object = list(self.tv_admin_db.USERS.find({"USER": user_name}, projection={"_id": 0}))[0]
            current_assignments = user_object["ASSIGNMENTS"]
            current_assigned_dbs = [assignment['PROJECT_NAME'] for assignment in current_assignments]
            already_assigned = project_db_name in current_assigned_dbs
            if already_assigned:
                denied_message = "DENIED: Users cannot be assigned the same roles to a projects they are already\n "\
                                 "Assigned to users also cannot be granted multiple roles to a single project"
                return denied_message, None
            else:
                # grant role by specifying role and db
                self.tv_admin_db.command(
                    "grantRolesToUser", user_name,
                    roles=[{"role": new_role, "db": project_db_name}])
                # add new role to assignment list
                current_assignments.append({"PROJECT_NAME": project_db_name, "ROLE": new_role})
                # update user doc with new assignment
                self.tv_admin_db.USERS.update_one({"USER": user_name},
                                                  {"$set": {"ASSIGNMENTS": current_assignments}})
                approved_message1 = "User Info. Updated in Admin database: \n", user_object
                # Add contact doc in newly granted db (re run previous code to refresh db)
                project_db_user_object = user_object
                del project_db_user_object['ASSIGNMENTS']
                self.client.project_db_name.Contact.insert_one(project_db_user_object)
                approved_message2 = "User contact added in ", project_db_name, " database:\n", project_db_user_object
                return approved_message1, approved_message2
        else:
            denied_message = "Invalid User name, User name does not exist"
            return denied_message, None

    # Keep for testing purposes 
    def test_create_new_db(self, db_name, default_contact_username):
        # The default contact_parameter will take in a user_name, get the contact doc from TV_ADMIN and insert
        # it into the contact collection of a new db, this is a bit different from using initialize project

        system_dbs_list = list(self.client.list_databases())
        db_exists = db_name in system_dbs_list

        if db_exists:
            contact_doc = list(self.tv_admin_db.USERS.find({"USER": default_contact_username}))[0]
            new_db = self.client[db_name]

            new_db.command(
                "createRole",
                "Project Lead",
                privileges=[],
                roles=["readWrite", "dbAdmin"]
            )

            new_db.command(
                "createRole",
                "Project Analyst",
                privileges=[],
                roles=["readWrite"]
            )
            contact_col = new_db['Contact']
            contact_col.insert_one(contact_doc)
            approved_message = db_name, "database has been created\n" + default_contact_username, "Contact has been " \
                               "uploaded to", db_name, "database"
        else:
            denied_message = "This database name is already in use"
            return denied_message
        
    #def tv_admin_db_revoke_role_to_user

