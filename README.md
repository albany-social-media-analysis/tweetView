# TweetView

Tweet view is an online web application system designed to provide the ability to label twitter post data in a survey format. This application allows the user to upload their own twitter data and set a validation schema for a particular dataset. In TweetView, datasets are divided into its own individual projects, which are led by project leads who monitor a project’s progression, and the uploaded datasets are surveyed by project analysts (and project leads) that are assigned to a particular project.

TweetView is built using the Flask website framework and uses MongoDB on the backend for data management purposes. Though TweetView runs on a MongoDB interface, datasets can be upload in other of formats such as JSON, CSV, and TXT.  

## TweetView requirements

At a minimum, in order to use TweetView, you should: 
•	Have a private email account

•	Access to a computer and stable internet connectivity 

•	Basic computer and web browsing literacy 

•	Rudimentary Knowledge of data and file management 

At a maximum: 

•	Comfortably able using MongoDB command line tool

•	Comfortably able to use and perform various terminal commands 


## How to use

In order to use TweetView, you will have to first sign up via the TweetView registration page. 

Once the sign up form is filled and submitted through the webpage successfully, an email confirmation will be sent and the user’s information will be stored on the website’s main database system (“TV_ADMIN”) in the “USERS” collection. At this point, the user will still not be able to perform any of common functionalities as a role (and) or project assignment will be necessary. 

If the intended initial role for a user is to be a project lead, this role must be bestowed from the tweetView Admin user. On the other hand, if the intended initial role for the user is be a project analyst, the user will have to wait for a project lead to assign the user to a particular project before any analyst functionalities can be performed by the current user. 

All users can be assigned to multiple projects, and a project can have multiple project leads and analysts. Furthermore, a user can hold different roles for each project they are assigned to, meaning a user can be a project lead for one project and a project analyst in another. Additionally, project leads can perform supervisory and project analyst tasks (label provided data) to projects where they hold a project lead role.

## Registration

In order to register to use TweetView, you will have to first sign up via the TweetView registration page, http://127.0.0.1:5000/register, and provide a few personal information such as: first name, last name, username, password, and email address. 

NOTE: the password provided must be at least 7 characters in length and must contain at least one uppercase alphabetical and a numerical character.

## Tweet view roles

#### TweetView Admin 

There can only be one TweetView admin per TweetView system interface. The TweetView Admin role functions as any other admin system where the user has privileges to do anything across all projects (databases) in the TweetView interface. The TweetView Admin is the only role that has read/write privileges on all project and can override project leads. Though this role has many functionalities, it can only be accessed through the back via the command line tool, mainly used to do most of the initialization tasks when a TweetView interface system is initially set up.

    •	Role’s primary use cases:
    
        •		Assist in initializing TweetView system
        
        •       Grant project lead role to a user
        
        •		Provide new database for a requested project 
        
#### Project lead
The project lead role is a managerial responsibility for a given project. Where the admin role governs all projects, a project lead governs one (or multiple) specific projects that a user is assigned to. The project lead sole purpose is to provide maintenance and guidance for a given project. This can be done by adding to a project’s scope, sending emails to project analysts, keeping track of progress, or assist in labeling data.

      •		Role’s primary use cases: 
      
          •		Start a new project
          
          •		Assign project analyst to a project
          
          •		Upload datasets
          
          •		Provide validation schema for projects
          
          •		Label data
          
#### Project analyst

The sole purpose of a project analyst is to provide labels to the respective data based off the project’s validation schema provided by the project lead.

      •		Role’s primary use case: 
      
          •		Provide labels to data based off validation schema

## Setting up new projects

In order to create a new project, a project lead must provide a project name using the .initialize_new_project() method found within new_project_set_up.py. 

##Assigning users to a project

The only user’s that can assign other users to a given project through the TweetView browser are those that have been assigned project leads to the respective projects.

A project lead will have the ability to either force assign or notify qualified user on the landing page which will be accessible after successfully logging into TweetView. Project leads can only assign other users to projects that they are currently a lead of. Likewise, leads should have the ability to unassign users from a project as well. 

The role assignment process is a fairly simple point and click procedure whereas each list of users that are shown are possible candidates for a given project. The project lead will have the option to choose between force assigning or notifying a user to a requested project. “Force assign”, automatically assigns the selected user to the requested project and sends an email notifying the selected user as such, the user will then be able to perform all the tasks of an analyst for the requested project. To “notify” a user for a requested project, this will only send an email to the selected user, notifying the selected user of the project lead’s interest for the selected user’s assistance. 

## Labeling data

Labeling data for a project is a simple point and click procedure whereas the analyst selects the proper validation type corresponding to a given tweet. In order for a user to label data, the given project must have data stored to the project and a set validation schema provided from the project lead of the given project. A project lead should be able to provide a link for the validation schema upon creating a project which can then be seen and accessed via the project dashboard page for a given project.

### About Batches 

The tweet data provided during the labeling process will be divided into batches of 10. Once the analyst reaches the 10th tweet data within the batch, TweetView will show a flash warning message informing the user that he/she is on the final tweet data for the current batch. Once the final tweet data for the current batch is submitted, that batch of tweet data will be deleted from the user’s query collection and will be unable to return to and label any of the data from said batch, upon starting a new batch of tweet data. 



### About The Buttons 

Asides from selecting the appropriate validation type, the user will have the option of skipping the current tweet data (via the skip button), submitting the selected validations (via the submit button), or returning to the previous tweet data (via the previous button).

If the TweetView API call fails ( see /tweetView/mongo_config.py -> .get_tweet_html()), the TweetView labeling browser will render a HTML error message (indicating the tweet was deleted or a faulty tweet data mishap) where the analyst will then have the option of opting to return to the previous tweet data or continuing to the next tweet data (via the next button).
