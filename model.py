'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
import view
import random
import no_sql_db
import hashlib
import os

# Initialise our views, all arguments are defaults for the template
page_view = view.View()
current_user = []
header_switch = "header"

#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view("index", header=header_switch)

#-----------------------------------------------------------------------------
# Create User
#-----------------------------------------------------------------------------

def create_user_form():
    '''
        create_user_form
        Returns the view for the create_user_form
    '''
    return page_view("create_user", header=header_switch)

# Check the user credentials
def create_user(username, password):
    '''
        Create_user
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''
    global header_switch 

    #salt and hash the password
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    if no_sql_db.database.search_table_for_entry("users", "username", username) != None and no_sql_db.database.search_table_for_entry("users", "username", username) == no_sql_db.database.search_table_for_entry("users", "password", key):
        err_str = "User already exists. You have been logged in " + username + "!"
        header_switch = "login_header"
        return page_view.load_and_render("invalid_create_user", header=header_switch, reason=err_str)

    else:
        no_sql_db.database.create_table_entry('users', ["id", username, key, salt])
        current_user = no_sql_db.database.search_table_for_entry("users", "username", username)
        header_switch = "login_header"
        return page_view.load_and_render("valid_create_user", header=header_switch, name=username)


#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''
    global header_switch 

    #Check if user is in database or not  
    # Edge case would be where two users have the same password - add code to no_sql_db to then fix for this if this could happen
    if no_sql_db.database.search_table_for_entry("users", "username", username) == None:
        err_str = "User does not exist. Please create user first."
        return page_view("invalid_login", header=header_switch, reason=err_str)

    elif no_sql_db.database.search_table_for_entry("users", "username", username) == no_sql_db.database.search_table_for_entry("users", "password", password):
        current_user = no_sql_db.database.search_table_for_entry("users", "username", username)
        header_switch = "login_header"
        return page_view.load_and_render("valid_login", header=header_switch, name=username)
    
    elif no_sql_db.database.search_table_for_entry("users", "username", username) != no_sql_db.database.search_table_for_entry("users", "password", password):
        err_str = "Incorrect Password"
        return page_view("invalid_login", header=header_switch, reason=err_str)

    # By default assume good creds
    #login = False
     
#-----------------------------------------------------------------------------
# Logout
#-----------------------------------------------------------------------------

def logout_button():
    '''
        logout
        Returns the view for the logout_button
    '''
    return page_view("logout", header=header_switch)

# Check the login credentials
def logout_check():
    '''
        logout_check
        Checks user has been logged out

    '''
    global header_switch 
    header_switch = "header"

    return page_view("valid_logout", header=header_switch)

#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", header=header_switch, garble=about_garble())


# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass

#-----------------------------------------------------------------------------
# Friends list
#-----------------------------------------------------------------------------

def friends_list():
    #retrieve friends from database by user id

    data = [["Jane"], ["Alex"], ["Mark"]]
    result = page_view.render_list_as_table(data)
    return page_view("friends", header=header_switch, friends_html_table=result)

#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)