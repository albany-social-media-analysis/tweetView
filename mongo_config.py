port = 27018
user = 'root'
host = 'icehc1.arcc.albany.edu'
pwd = '3&NoIuwY0!4&'
amdin_database = 'TV_ADMIN'

tv_admin = 'TV_default_admin'
tv_admin_pwd = 'conspiracy123'

tv_email =  "tweetview.albany@gmail.com"
tv_email_pwd =  "Conspiracy123"
tv_email_port = 587
tv_email_server = "smtp.gmail.com"

account_registry_confirmation_message = "Congratulations you successfully signed up for TweetView"


# User assignment messages
def generate_assignment_message(assignee, force, project, project_lead, project_lead_email):

    force_assigned_message = assignee +" has be added to the  project: "+project+" an email has also been sent to the user"
    notify_message = "An Email has been sent to out to "+assignee+" to inquire project load availability"
    assigned_email_message = "This is email regarding your TweetView workload\n" \
                             "Project lead, "+project_lead+" has assigned you to project: "+project+".\n"\
                             "If you have any concerns please contact "+project_lead+" (EMAIL:"+project_lead_email+")."
    notify_email_message = "This is email regarding your TweetView workload\n" \
                           "Project lead, "+project_lead+" is sending an email notifying you for a " \
                           "possible analyst role assignment to  project: "+project+"."\
                           " Please contact "+project_lead+" (EMAIL: "+project_lead_email+") if you have the capable " \
                           "workload availability for this potential project assignment."
    if force:
        return force_assigned_message, assigned_email_message
    else:
        return notify_message, notify_email_message

