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
        print("GETTING ROOM ID: " + str(room_id))

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

#returns the username if authenticated otherwise returns False
def authenticate_session():

    user_session_id = request.get_cookie("user_session_id")
    if user_session_id not in sessions:
        return False
    else:
        return sessions[user_session_id]

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view("index",username=authenticate_session())
        

#-----------------------------------------------------------------------------
# Create User
#-----------------------------------------------------------------------------

def create_user_form():
    '''
        create_user_form
        Returns the view for the create_user_form
    '''

    if authenticate_session():
        return redirect('/')

    return page_view("create_user")
    

# Check the user credentials
def create_user(username, password, public_key):
    '''
        Create_user
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    if authenticate_session():
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
        no_sql_db.database.create_table_entry('users', [username, key, salt, '']) # note we start with empty public_key
        user_session_id = create_session(username, public_key)
        page_view.global_renders['username']=username
        return immediate_friends_list(user_session_id)
        #return page_view("create_user", username=username)

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''

    if authenticate_session():
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
    if authenticate_session():
        return redirect('/')

    #Check if user is in database or not  
    current_user = no_sql_db.database.search_table_for_entry("users", "username", username)
    if current_user == None:
        err_str = "User does not exist. Please create user first."
        return page_view("login", err=err_str)

    # Find the old salt and hash the new password
    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), current_user[2], 100000)
    
    if current_user[1] == new_key:
        user_session_id = create_session(username, public_key)
        return immediate_friends_list(user_session_id)
        #return page_view.load_and_render("login", username=username)
    else:
        err_str = "Incorrect Password. Please try again"
        return page_view("login", err=err_str)


#creates a session for the user via setting a cookie
def create_session(username, public_key):
    user_session_id = str(uuid.uuid4())
    #user_session_id = request.get_cookie("user_session_id")
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

    username = authenticate_session()

    if not username:
        return redirect('/')


    return page_view("logout",username=username)

# Check the login credentials
def logout_check():
    '''
        logout_check
        Checks user has been logged out
    '''
    if not authenticate_session():
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

    return page_view("about", garble=about_garble(),username=authenticate_session())


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
    
    current_user = authenticate_session()
    
    if not current_user:
        return redirect('/')

    data = no_sql_db.database.select_all_table_values("users","username")
    data.remove([current_user])
    print(data)
    
    return page_view("friends", friends_list=data,username=current_user)

def immediate_friends_list(user_session_id):
    current_user = sessions[user_session_id]
    data = no_sql_db.database.select_all_table_values("users","username")
    data.remove([current_user])

    return page_view("friends", friends_list=data,username=current_user)

#-----------------------------------------------------------------------------
# Messaging
#-----------------------------------------------------------------------------

def chat(friend):

    username = authenticate_session()

    if not username or friend is None:
        return redirect('/')
    
    return page_view("chat",friend=friend,username=username,chat=True)    

def connect_socket(sid) :
    sid_map[sid] = sessions[request.get_cookie("user_session_id")]
    return authenticate_session()

def join_chat(data,sid,sio):
    username = authenticate_session()
    friend_pk = no_sql_db.database.search_table_for_entry("users", "username", data['friend'])[3]
    print(friend_pk)
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