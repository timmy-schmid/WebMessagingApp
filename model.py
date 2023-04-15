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
import uuid
import re
import time
from bottle import redirect,request, response

MAX_PWD_LENGTH = 8

page_view = view.View()

sessions = {}

#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def get_session_username():

    user_session_id = request.get_cookie("user_session_id")
    if user_session_id not in sessions:
        return
    else:
        return sessions[user_session_id]

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view("index",username=get_session_username())

#-----------------------------------------------------------------------------
# Create User
#-----------------------------------------------------------------------------

def create_user_form():
    '''
        create_user_form
        Returns the view for the create_user_form
    '''

    if get_session_username():
        return redirect('/')

    return page_view("create_user")

# Check the user credentials
def create_user(username, password):
    '''
        Create_user
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    if get_session_username():
        return redirect('/')
    
    # Salt and hash the password
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    
    if len(username) == 0 :
        err_str = "Username cannot be empty. Please try again"
        return page_view("create_user", err=err_str)
    
    elif username == password:
        err_str = "Username cannot be the same as password" 
        return page_view("create_user", err=err_str)
    
    elif len(password) < MAX_PWD_LENGTH:
        err_str = "Password must be at least 8 characters long. Please try again" 
        return page_view("create_user", err=err_str)
    
    elif re.compile('[^0-9a-zA-Z]+').search(password) == None:
        err_str = "Password must contain a special character. Please try again" 
        return page_view("create_user", err=err_str)
        
    elif no_sql_db.database.search_table_for_entry("users", "username", username):
        err_str = "A user already exists with this username. Please choose a different username."
        return page_view("create_user", err=err_str)
    
    else:
        no_sql_db.database.create_table_entry('users', ["id", username, key, salt])
        create_session(username)
        return page_view("create_user", username=username)

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''

    if get_session_username():
        return redirect('/')

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
    if get_session_username():
        return redirect('/')

    #Check if user is in database or not  
    current_user = no_sql_db.database.search_table_for_entry("users", "username", username)
    if current_user == None:
        err_str = "User does not exist. Please create user first."
        return page_view("login", err=err_str)

    # Find the old salt and hash the new password
    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), current_user[3], 100000)
    
    if current_user[2] == new_key:
        create_session(username)
        return page_view.load_and_render("login", username=username)
    else:
        err_str = "Incorrect Password. Please try again"
        return page_view("login", err=err_str)


#creates a session for the user via setting a cookie
def create_session(username):
    user_session_id = request.get_cookie("user_session_id")
    user_session_id = str(uuid.uuid4())
    sessions[user_session_id] = username
    response.set_cookie("user_session_id",user_session_id)

#-----------------------------------------------------------------------------
# Logout
#-----------------------------------------------------------------------------

def logout_button():
    '''
        logout
        Returns the view for the logout_button
    '''
    if not get_session_username():
        return redirect('/')


    return page_view("logout",username=get_session_username())

# Check the login credentials
def logout_check():
    '''
        logout_check
        Checks user has been logged out
    '''
    if not get_session_username():
        return redirect('/')

    user_session_id = request.get_cookie("user_session_id")
    sessions.pop(user_session_id)

    return redirect("/")

#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''

    return page_view("about", garble=about_garble(),username=get_session_username())


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
def friends_data():
    current_user = get_session_username()

    if not current_user:
        return redirect('/')

    data = no_sql_db.database.select_all_table_values("users","username")
    print(data)
    print(type(data))
    data.remove([current_user])
    return data

def friends_list():
    #retrieve friends from database by user id
    """
    current_user = get_session_username()

    if not current_user:
        return redirect('/')

    data = no_sql_db.database.select_all_table_values("users","username")
    print(data)
    print(type(data))
    data.remove([current_user])
    """
    return page_view("friends", friends_list=friends_data(),username=get_session_username())

#-----------------------------------------------------------------------------
# Messaging
#-----------------------------------------------------------------------------

def chat(friend):
    if not get_session_username() or friend is None:
        return redirect('/')
    
    return page_view("chat",friend=friend,username=get_session_username())    


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)