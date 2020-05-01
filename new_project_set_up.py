from pymongo import MongoClient
from pathlib import Path
import mongo_config


# Come up with a way to login into a database that has just been created by project lead
# Add checks to see if user status is authorized to do so in this database then give access to default admin
def initialize_new_project(project_name, project_lead_user_name):
    default_client = MongoClient('TV_ADMIN', username=mongo_config.tv_admin, password=mongo_config.tv_admin_pwd,
                                 port=mongo_config.port)
    tv_username_list = default_client.TV_ADMIN.command('userInfo')['users']
    tv_username_list = [userinfo['user'] for userinfo in tv_username_list]
    if project_lead_user_name in tv_username_list:
        new_project = default_client[project_name]
        # create tv Roles in new project db
        new_project.command(
            "createRole",
            "Project Lead",
            privileges=[],
            roles=["dbOwner", "dbAdmin"])
        new_project.command(
            "createRole",
            "Project Analyst",
            privileges=[],
            roles=["readWrite"])
        contact_collection = new_project['user_contacts']
        # grab first name,last name, phone, email from admin db user collection
        # this will be the first doc for the database
        pj_lead_contact_doc = list(default_client.TV_ADMIN.USERS.find({"USER": project_lead_user_name}))[0]

        # update assignment field in admin contacts db
        current_assignments = pj_lead_contact_doc['ASSIGNMENTS']
        current_assignments.append({"PROJECT_NAME": project_name, "ROLE": "Project Lead"})
        default_client.TV_ADMIN.USERS.update_one({"USERS": project_lead_user_name},
                                                 {"$set": {"ASSIGNMENTS": current_assignments}})

        del pj_lead_contact_doc['ASSIGNMENTS']
        contact_collection.insert_one(pj_lead_contact_doc)
        # grant the user pj_lead the privileges to new project from admin db
        default_client.TV_ADMIN.command("grantRolesToUser", project_lead_user_name,
                                        roles=[{"role": "Project Lead", "db": project_name}])
        approved_message = project_name, "successfully created with", project_lead_user_name, "the lead"
        approved_message_2 = project_lead_user_name + "'s contact doc has been updated in admin database"
        approved_message_3 = project_lead_user_name + "'s information has been added to", project_name,"'s " \
                                                      "contact collection"
        return approved_message, approved_message_2, approved_message_3, pj_lead_contact_doc
    else:
        denied_message = 'This user does not exist, enter a user name that is already registered'
        return denied_message, None, None, None

