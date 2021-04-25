from flask_wtf import FlaskForm
from wtforms import (StringField,BooleanField,DateTimeField,RadioField,
                    SelectField,TextField,TextAreaField,SubmitField,
                    PasswordField, HiddenField)
from wtforms.validators import DataRequired, Optional, length, EqualTo

class UserLoginForm(FlaskForm):
    # These fields will be used for old and new entries
    user_name = StringField('User Name', validators=[DataRequired()])
    pass_word = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField()

class UserRegisterForm(FlaskForm):
    # The other fields are used for new entries only
    first_name = StringField('First Name', validators=[Optional()])
    last_name = StringField('Last Name',validators=[Optional()])
    new_register_user_name = StringField('User Name', validators=[DataRequired()])
    new_register_pass_word = PasswordField('PassWord', validators=[DataRequired(),
            EqualTo('new_register_pass_word', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    email = StringField('Enter E-Mail Adress')
    # may have to add database and roles in database instead
    role = SelectField('Select a Role (WARNING: Supervisor will have to apporve'
            'role)', choices=[(None, '--- NONE ---'),('admin','Tool Admin'),
                        ('lead','Project Lead'), ('analyst','Project Lead')])
    submit = SubmitField()
    # The 3 submit fields will be used to differentiate each of the actions and
    # reidrections to other pages on the site

class CredentialRetreival(FlaskForm):

    retrieval_type = SelectField('What information did you forget?',
                     choices=[('usr', 'My user name'), ('pwd', 'My password')])
    forgot_user_name = StringField('User Name', validators=[DataRequired()])
    user_email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField()

class ChangeLoginInfo(FlaskForm):

    account_option = SelectField('What do you want to update',
    choices=[('usr', 'My user name'), ('pwd', 'My Password'),
             ('pj_request', 'Request new project'), ('contact', 'Change Contact Information')])
    changed_user_name = StringField('Enter your new user name')
    old_pass_word = PasswordField('Enter your current password')
    changed_pass_word = PasswordField('Enter your new password',
    validators=[EqualTo('confirmed_changed_pass_word',
    message='Passwords do not match')])
    confirmed_changed_pass_word = PasswordField()
    new_contact = StringField('Enter a new E-Mail Adress')
    submit = SubmitField()

class AssignUserButton(FlaskForm):
    # This class will only hold a button form for when a Project Lead needs to assign a new analyst
    # This could also be used for another purpose down the line for a similar circumstance
    submit_request = SubmitField()
    request_type = RadioField(choices=[('force', 'Force Assign This Analyst'), ('notify', 'Notify This Analyst')])
    analyst = HiddenField()
    selected_project = HiddenField()

class ProjectModifyer(FlaskForm):

    data_modification_action = SelectField("How do you want to update the project's database",
                                           choices=[('upload', 'Upload dataset'), ('delete', 'Delete data'),
                                                    ('download', 'Download Dataset')])
    # enum
    enum_label = StringField('Enter a label for the options field')
    validator_option_1 = StringField()
    validator_option_2 = StringField()
    validator_option_3 = StringField()
    enum_description = StringField('Enter a description for this field')
    enum_required = RadioField('Should this field be required for labeling submission',
                                    choices=[('Required Field', 'required'),
                                             ('Optional Field', 'optional')])

    # int
    int_label = StringField('Enter a label for the integer selection field')
    int_description = StringField('Enter a description for this field')
    int_required = RadioField('Should this field be required for labeling submission',
                                    choices=[('Required Field', 'required'),
                                             ('Optional Field', 'optional')])

    # bool
    bool_label = StringField('Enter a label for the boolean field')
    bool_description = StringField('Enter a description for this field')
    bool_required = RadioField('Should this field be required for labeling submission',
                                    choices=[('Required Field', 'required'),
                                             ('Optional Field', 'optional')])

    # text
    text_label = StringField('Enter a label for the comment field')
    text_description = StringField('Enter a description for this field')
    text_required = RadioField('Should this field be required for labeling submission',
                                    choices=[('Required Field', 'required'),
                                             ('Optional Field', 'optional')])


    submit = SubmitField()