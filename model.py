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
import socketio
from bottle import redirect,request, response

MAX_PWD_LENGTH = 8

page_view = view.View()

USERNAME = 0
EMAIL = 1
PASSWORD = 2
SALT = 3
PK = 4
IS_ADMIN=5
IS_MUTED = 6


#Rooms Singletons
class Rooms:
    def __init__(self):
        self.users = {}
        self.counter = 0

    #gets room_id between two parties. If it doesn't exist we create the room id
    def get_room_id(self,username,friend):
        if self.users.get(username, None) is None:
            self.users[username] = {}

        if self.users.get(friend, None) is None:
            self.users[friend] = {}

        room_id = self.users[friend].get(username, None)

        if room_id is not None: #if the room_id exists already then we add the room_id for the current user
            self.users[username][friend] = room_id
        else:
            room_id = self.counter
            self.users[username][friend] = self.counter
            self.users[friend][username] = self.counter
            self.counter+=1

        return room_id
    
    def remove_all_rooms(self,sid,sio):
        current_username = sid_map(sid)
        for friend in self.users[current_username]:
            room_id = self.remove_room_id(self,current_username,friend)
            sio.leave_room(sid,room_id)
            sio.emit('leave_announcement', {'username': current_username }, room=room_id)

    #removes room_id as the the users session is ending.
    #Note, we don't delete the friends room as they may still be connected
    def remove_room_id(self,username,friend):
        return self.users[username].pop(friend,None)

sessions = {}
sid_map = {}
rooms = Rooms()

#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

#returns the username if authenticated and if admin otherwise returns False, False
def authenticate_session():

    user_session_id = request.get_cookie("user_session_id")
    if user_session_id not in sessions:
        return False, False
    else:
        current_user = no_sql_db.database.search_table_for_entry("users", "username", sessions[user_session_id])
        return sessions[user_session_id], current_user[IS_ADMIN]


def index():
    '''
        index
        Returns the view for the index
    '''
    if authenticate_session()[USERNAME] == False:
        return page_view("index",username=authenticate_session()[USERNAME], admin=False)
    
    username, is_admin = authenticate_session()
    return page_view("index",username=username, admin=is_admin)

#-----------------------------------------------------------------------------
# Forgot Pwd
#-----------------------------------------------------------------------------
def forgot_details():
    '''
        create_user_form
        Returns the view for the create_user_form
    '''

    if authenticate_session()[USERNAME]:
        return redirect('/')

    return page_view("forgot_details")

def forgot_details_post():
    '''
        create_user_form
        Returns the view for the create_user_form
    '''

    if authenticate_session()[USERNAME]:
        return redirect('/')

    return page_view("forgot_details", success=True)
    
#-----------------------------------------------------------------------------
# Create User
#-----------------------------------------------------------------------------

def create_user_form():
    '''
        create_user_form
        Returns the view for the create_user_form
    '''

    if authenticate_session()[USERNAME]:
        return redirect('/')

    return page_view("create_user",)
    

# Check the user credentials
def create_user(username, email, password, confirm_password, public_key):
    '''
        Create_user
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''


    if authenticate_session()[1]:
        return redirect('/')
    
    # Salt and hash the password
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    
    if len(username) == 0 :
        err_str = "Username cannot be empty. Please try again"
        return page_view("create_user", err=err_str)
    elif len(email) == 0:
        err_str = "Email cannot be empty. Please try again"
        return page_view("create_user", err=err_str)
    elif no_sql_db.database.search_table_for_entry("users", "username", username):
        err_str = "A user already exists with this username. Please choose a different username."
        return page_view("create_user", err=err_str)
    elif no_sql_db.database.search_table_for_entry("users", "email", email):
        err_str = "A user with this email already exists. Please choose a different email address."
        return page_view("create_user", err=err_str)
    elif username == password:
        err_str = "Username cannot be the same as password"
        return page_view("create_user", err=err_str)
    elif password != confirm_password:
        err_str = "Password entries are different. Please confirm your password and try again." 
        return page_view("create_user", err=err_str)
    elif len(password) < MAX_PWD_LENGTH:
        err_str = "Password must be at least 8 characters long. Please try again" 
        return page_view("create_user", err=err_str)
    elif re.compile('[^0-9a-zA-Z]+').search(password) == None:
        err_str = "Password must contain a special character. Please try again" 
        return page_view("create_user", err=err_str)
    else:
        no_sql_db.database.create_table_entry('users', [username, email,key, salt, '', False, False]) # note we start with empty public_key
        user_session_id = create_session(username, public_key)
        page_view.global_renders['username']=username
        return page_view("login", username=username)

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''

    if authenticate_session()[USERNAME]:
        return redirect('/')

    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password, public_key):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''
    
    if authenticate_session()[USERNAME]:
        return redirect('/')

    #Check if user is in database or not  
    current_user = no_sql_db.database.search_table_for_entry("users", "username", username)
    if current_user == None:
        err_str = "User does not exist. Please create user first."
        return page_view("login", err=err_str)

    # Find the old salt and hash the new password
    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), current_user[SALT], 100000)
    is_admin = current_user[IS_ADMIN]

    if current_user[PASSWORD] == new_key:
        user_session_id = create_session(username, public_key)
        return page_view("login", username=current_user[USERNAME], admin=is_admin)    
    else: 
        err_str = "Incorrect Password. Please try again"
        return page_view("login", err=err_str)


#creates a session for the user via setting a cookie
def create_session(username, public_key):
    user_session_id = str(uuid.uuid4())
    sessions[user_session_id] = username
    response.set_cookie("user_session_id",user_session_id)
    no_sql_db.database.update_table_val("users","username",username, "public_key", public_key)
    return user_session_id

#-----------------------------------------------------------------------------
# Logout
#-----------------------------------------------------------------------------

def logout_button():
    '''
        logout
        Returns the view for the logout_button
    '''

    username, is_admin = authenticate_session()

    if not username:
        return redirect('/')

    return page_view("logout",username=username, admin=is_admin)

# Check the login credentials
def logout_check():
    '''
        logout_check
        Checks user has been logged out
    '''
    if not authenticate_session()[USERNAME]:
        return redirect('/')

    user_session_id = request.get_cookie("user_session_id")
    sessions.pop(user_session_id)

    return redirect("/")

#-----------------------------------------------------------------------------
# Account Settings
#-----------------------------------------------------------------------------
def account_settings():
    '''
        about
        Returns the view for the account settings page
    '''
    username, is_admin = authenticate_session()

    if not username:
        return redirect('/')

    return page_view("account_settings", username=username, admin=is_admin)

    
#-----------------------------------------------------------------------------

# Check the username
def change_username(new_username, public_key):
    '''
        change_username
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''
    username, is_admin = authenticate_session()

    
    if not username:
        return redirect('/')
        
    if len(new_username) == 0 :
        err_str = "Username cannot be empty. Please try again"
        return page_view("account_settings", err_username=err_str, username=username, admin=is_admin)
    
    elif username == new_username:
        err_str = "New username is the same as your current username. Choose a new username." 
        return page_view("account_settings", err_username=err_str, username=username, admin=is_admin)
    
    elif no_sql_db.database.search_table_for_entry("users", "username", new_username):
        err_str = "A user already exists with this username. Please choose a different username."
        return page_view("account_settings", err_username=err_str, username=username, admin=is_admin)
    
    else:
        #Remove current session and create a new one with the new public key
        user_session_id = request.get_cookie("user_session_id")
        sessions.pop(user_session_id)
        no_sql_db.database.update_table_val('users', 'username', username, 'username', new_username)
        create_session(new_username, public_key)

        success_str = "Your username has been updated to: " + new_username 
        return page_view("account_settings", success_username=success_str, username=new_username, admin=is_admin)

#-----------------------------------------------------------------------------

# Check the password
def change_password(current_password, new_password,confirm_new_password):
    '''
        change_password
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''
    username,is_admin = authenticate_session()

    if not username:
        return redirect('/')
        

    #Check if user is in database or not  
    current_user = no_sql_db.database.search_table_for_entry("users", "username", username)

    # Find the old salt and hash the new password
    new_key = hashlib.pbkdf2_hmac('sha256', current_password.encode('utf-8'), current_user[SALT], 100000)

    # Salt and hash the new password
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), salt, 100000)
    
    if current_user[PASSWORD] == new_key:
        if username == new_password:
            err_str = "Username cannot be the same as new password" 
            return page_view("account_settings", err_password=err_str, username=username, admin=is_admin)
        
        if current_password == new_password:
            err_str = "New password is the same as your current password. Choose a new password." 
            return page_view("account_settings", err_password=err_str, username=username, admin=is_admin)
        
        elif len(new_password) < MAX_PWD_LENGTH:
            err_str = "New password must be at least 8 characters long. Please try again" 
            return page_view("account_settings", err_password=err_str, username=username, admin=is_admin)
        elif new_password != confirm_new_password:
            err_str = "New passwords do not match. Please confirm your password and try again." 
            return page_view("account_settings", err_password=err_str, username=username, admin=is_admin)
        
        elif re.compile('[^0-9a-zA-Z]+').search(new_password) == None:
            err_str = "New password must contain a special character. Please try again" 
            return page_view("account_settings", err_password=err_str, username=username, admin=is_admin)
        
        else:
            no_sql_db.database.update_table_val('users', 'username', username, 'password', key)
            no_sql_db.database.update_table_val('users', 'username', username, 'salt', salt)
            
            success_str = "Your password has been updated." 
            return page_view("account_settings", success_password=success_str, username=username, admin=is_admin)
    
    else:
        err_str = "Incorrect current password. Please try again"
        return page_view("account_settings", err_password=err_str, username=username, admin=is_admin)
    

#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''

    username, is_admin = authenticate_session()
    return page_view("about", garble=about_garble(),username=username, admin=is_admin)


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
# Help & Knowledge articles
#-----------------------------------------------------------------------------

def help(article_title):
    '''
        help
        Returns the view for the help page
    '''
    username, is_admin = authenticate_session()
    articles = no_sql_db.database.select_all_table_values("help_articles", "title")

    if article_title is not None:
        article_content = no_sql_db.database.search_table_for_entry("help_articles", "title",article_title)[1]
    else:
        article_content = None       
    return page_view("help",article_title=article_title, article_content=article_content,articles=articles,username=username, admin=is_admin)

def remove_help_article(article_title):
    username, is_admin = authenticate_session()

    if not is_admin:
        return redirect('/')

    current_article = no_sql_db.database.search_table_for_entry("help_articles", "title",article_title)
    no_sql_db.database.remove_table_entry('help_articles', current_article)
    articles = no_sql_db.database.select_all_table_values("help_articles", "title")
    return page_view("help",article_title=article_title, article_content=None,articles=articles,username=username, admin=is_admin)

def add_help_article(article_title, article_content):
    username, is_admin = authenticate_session()

    if not is_admin:
        return redirect('/')
    
    no_sql_db.database.create_table_entry('help_articles', [article_title,article_content])
    articles = no_sql_db.database.select_all_table_values("help_articles", "title")
    return page_view("help",article_title=article_title, article_content=None,articles=articles,username=username, admin=is_admin)


def knowledge(article_title):
    '''
        knowledge
        Returns the view for the knowledge base page
    '''
    username, is_admin = authenticate_session()
    
    is_muted = no_sql_db.database.search_table_for_entry("users", "username", username)[IS_MUTED]

    if not username:
        return redirect('/')
    articles = no_sql_db.database.select_all_table_values("knowledge_articles", "title")

    if article_title is not None:
        article_content = no_sql_db.database.search_table_for_entry("knowledge_articles", "title",article_title)[1]
        author = no_sql_db.database.search_table_for_entry("knowledge_articles", "title",article_title)[2]
        is_anonymous = no_sql_db.database.search_table_for_entry("knowledge_articles", "title",article_title)[3]
        comments = no_sql_db.database.search_table_for_entry("knowledge_articles", "title",article_title)[4]

    else:
        article_content = None
        author = None   
        is_anonymous = False
        comments = None
    
    return page_view("knowledge",article_title=article_title, article_content=article_content,
                     author=author,anonymous=is_anonymous, muted=is_muted, articles=articles,
                     username=username, admin=is_admin, comments=comments)

def remove_knowledge_article(article_title):
    username, is_admin = authenticate_session()

    if not username:
        return redirect('/')

    current_article = no_sql_db.database.search_table_for_entry("knowledge_articles", "title",article_title)
    no_sql_db.database.remove_table_entry('knowledge_articles', current_article)
    articles = no_sql_db.database.select_all_table_values("knowledge_articles", "title")
    return page_view("knowledge",article_title=article_title, article_content=None,articles=articles,username=username, admin=is_admin)

def add_knowledge_article(article_title, article_content, anonymous):
    username, is_admin = authenticate_session()

    if not username:
        return redirect('/')
    
    is_anonymous = False
    if anonymous == "True":
        is_anonymous = True

    no_sql_db.database.create_table_entry('knowledge_articles', [article_title, article_content, username, is_anonymous, []])
   
    articles = no_sql_db.database.select_all_table_values("knowledge_articles", "title")

    return page_view("knowledge", article_title=article_title, article_content=None, articles=articles, username=username, admin=is_admin)

def post_comment(article_title, user_comment):
    username, is_admin = authenticate_session()

    current_article_comments = no_sql_db.database.search_table_for_entry("knowledge_articles", "title", article_title)[4]

    comment_string = username + ": " + user_comment
    current_article_comments.append(comment_string)

    no_sql_db.database.update_table_val("knowledge_articles", "title", article_title, 'comments', current_article_comments)
    
    return knowledge(article_title)


#-----------------------------------------------------------------------------
# Friends list
#-----------------------------------------------------------------------------

def get_user_data(current_user):
    data = no_sql_db.database.select_all_table_values("users","username")
    data.remove(current_user)

    #Remove admin?
    """if current_user != "Admin":
        data.remove("Admin")"""

    return data

def immediate_friends_list(user_session_id):
    current_user = sessions[user_session_id]
    data = get_user_data(current_user)

    return page_view("chat", friends_list=data,username=current_user)

#-----------------------------------------------------------------------------
# Edit Users
#-----------------------------------------------------------------------------
def edit_users():
    '''
        about
        Returns the view for the account settings page
    '''

    current_user, is_admin = authenticate_session()
    
    if not current_user:
        return redirect('/')
    
    data = get_user_data(current_user)

    mute_list = []
    for user_entry in data:
        if no_sql_db.database.search_table_for_entry("users", "username", user_entry)[IS_MUTED] == True:
            mute_list.append(user_entry)

    return page_view("edit_users", user_list=data,username=current_user, mute_list=mute_list, admin=is_admin)

def remove_user(user):
    username, is_admin = authenticate_session()
    current_user = no_sql_db.database.search_table_for_entry("users", "username", user)

    no_sql_db.database.remove_table_entry('users', current_user)
    data = get_user_data(username)

    success_string = user + " has been removed."

    mute_list = []
    for user_entry in data:
        if no_sql_db.database.search_table_for_entry("users", "username", user_entry)[IS_MUTED] == True:
            mute_list.append(user_entry)

    return page_view("edit_users", user_list=data, username=username, admin=is_admin, mute_list=mute_list, success=success_string)

def mute_user(user):
    username, is_admin = authenticate_session()

    no_sql_db.database.update_table_val("users","username", user, "is_muted", True)

    success_string = user + " has been muted."

    data = get_user_data(username)

    mute_list = []
    for user_entry in data:
        if no_sql_db.database.search_table_for_entry("users", "username", user_entry)[IS_MUTED] == True:
            mute_list.append(user_entry)

    return page_view("edit_users", user_list=data, username=username, admin=is_admin, mute_list=mute_list, success=success_string)

def unmute_user(user):
    username, is_admin = authenticate_session()

    no_sql_db.database.update_table_val("users","username", user, "is_muted", False)

    success_string = user + " has been unmuted."

    data = get_user_data(username)

    mute_list = []
    for user_entry in data:
        if no_sql_db.database.search_table_for_entry("users", "username", user_entry)[IS_MUTED] == True:
            mute_list.append(user_entry)

    return page_view("edit_users", user_list=data, username=username, admin=is_admin, mute_list=mute_list, success=success_string)

#-----------------------------------------------------------------------------
# Messaging
#-----------------------------------------------------------------------------

def chat(friend):

    #retrieve friends from database by user id
    current_user, is_admin = authenticate_session()
    
    if not current_user:
        return redirect('/')

    data = get_user_data(current_user)

    if friend:
        chat = True
    else:
        chat = False

    return page_view("chat", friend=friend,friends_list=data, chat=chat, username=current_user, admin=is_admin)


def connect_socket(sid) :
    sid_map[sid] = sessions[request.get_cookie("user_session_id")]
    return authenticate_session()[USERNAME]

def join_chat(data,sid,sio):
    username = authenticate_session()[USERNAME]
    friend_pk = no_sql_db.database.search_table_for_entry("users", "username", data['friend'])[PK]
    room_id = rooms.get_room_id(username,data['friend'])
    sio.enter_room(sid,room_id)
    sio.emit('join_announcement', {'username': username, 'friend_pk': friend_pk}, room=room_id) 

def send_msg(data,sid,sio):
    room_id = rooms.get_room_id(data['username'],data['friend'])
    sio.emit('recieve_msg', {'msg': data['msg'], 'username':data['username']}, room=room_id, skip_sid=sid)

def leave_chat(data,sid,sio):
    room_id = rooms.remove_room_id(data['username'],data['friend'])
    sio.leave_room(sid,room_id)
    sio.emit('leave_announcement', {'username': data['username'] }, room=room_id)

def disconnect(sid,sio):
    rooms.remove_all_rooms(sid,sio)

#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)