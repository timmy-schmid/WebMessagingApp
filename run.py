'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import Bottle, route, get, post, error, request, redirect, static_file
import model
import eventlet
import socketio

#socket setup
server = Bottle()
sio = socketio.Server(logger=True,engineio_logger=True, async_mode='eventlet')
server.wsgi = socketio.WSGIApp(sio, server.wsgi)

#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@server.route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

# Allow CSS
@server.route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

# Allow javascript
@server.route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Sockets
#-----------------------------------------------------------------------------

@sio.event
def connect(sid, environ):
    return model.connect_socket(sid)

@sio.event
def join_chat(sid, data):
    model.join_chat(data,sid,sio)
    
@sio.event
def send_msg(sid, data):
    model.send_msg(data,sid,sio)

@sio.event
def leave_chat(sid, data):
    model.leave_chat(data,sid,sio)

#@sio.event
#def disconnect(sid):
    #model.disconnect(sid,sio)


#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to index
@server.get('/')
@server.get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''

    return model.index()

# Display the create user page
@server.get('/create_user')
def get_create_user_controller():
    '''
        get_create_user
        
        Serves the login page
    '''
    return model.create_user_form()

# Attempt to create user
@server.post('/create_user')
def post_create_user():
    '''
        post_create_user
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    email = request.forms.get("email");
    password = request.forms.get('password')
    confirm_password = request.forms.get('confirm_password')
    if request.forms.get("public_key") is not None:
        public_key = request.forms.get("public_key").replace("\r","") #hack to remove extra \r that are added with POST request
    else:
        public_key = None
    # Call the appropriate method
    return model.create_user(username,email, password, confirm_password, public_key)

# Display the login page

@server.get('/forgot_details')
def forgot_details():
    return model.forgot_details()

@server.post('/forgot_details')
def forgot_details():
    return model.forgot_details_post()

@server.get('/chat')
def get_chat():

    friend = request.query.get('friend')

    return model.chat(friend)

@server.post('/chat')
def close_chat():
    return redirect('/')


@server.get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    return model.login_form()

# Attempt the login
@server.post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    if request.forms.get("public_key") is not None:
        public_key = request.forms.get("public_key").replace("\r","") #hack to remove extra \r that are added with POST request
    else:
        public_key = None

    
    # Call the appropriate method
    return model.login_check(username, password, public_key)

# Display the logout page
@server.get('/logout')
def get_logout_controller():
    '''
        get_login
        
        Serves the login page
    '''
    return model.logout_button()

# Attempt the logout
@server.post('/logout')
def post_logout():
    '''
        post_logout
        
        Handles logout attempts
    '''
    
    # Call the appropriate method
    return model.logout_check()

@server.get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    return model.about()

@server.get('/account_settings')
def get_account_settings():
    '''
        get_account_settings
        
        Serves the account_settings page
    '''
    return model.account_settings()

# Attempt the username
@server.post('/change_username')
def post_change_username():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    new_username = request.forms.get('new_username')
    public_key = request.forms.get('public_key')
    
    # Call the appropriate method
    return model.change_username(new_username, public_key)

# Attempt the change_password
@server.post('/change_password')
def post_change_password():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    current_password = request.forms.get('current_password')
    new_password = request.forms.get('new_password')
    confirm_new_password = request.forms.get('confirm_new_password')
    
    # Call the appropriate method
    return model.change_password(current_password, new_password,confirm_new_password)

@server.post('/help')
def post_help():
    '''
        post_help
        
        Handles additions and deletions of articles
    '''
    # Handle the form processing
    article_title = request.forms.get('article_title')
    # Call the appropriate method
    if request.forms.get("remove") == "remove":
        return model.remove_help_article(article_title)
    
    if request.forms.get("add") == "add":
        article_content = request.forms.get('article_content')
        return model.add_help_article(article_title,article_content)
    

@server.get('/help')
def get_help():
    '''
        get_help
        
        Serves the help / FAQ page.
    '''
    article = request.query.get('article')
    return model.help(article)

@server.post('/knowledge')
def post_knowledge():
    '''
        post_knowledge
        
        Handles additions and deletions of articles of knowledge page
    '''
    # Handle the form processing
    article_title = request.forms.get('article_title')

    # Call the appropriate method
    if request.forms.get("remove") == "remove":
        return model.remove_knowledge_article(article_title)
    
    if request.forms.get("add") == "add":
        article_content = request.forms.get('article_content')
        is_anonymous = request.forms.get('is_anonymous')
        return model.add_knowledge_article(article_title, article_content, is_anonymous)

    if request.forms.get("comment") == "comment":
        user_comment = request.forms.get('user_comment')
        return model.post_comment(article_title, user_comment)

@server.get('/knowledge')
def get_knowledge():
    '''
        knowledge
        
        Serves the knowledge base page.
    '''
    article = request.query.get('article')
    return model.knowledge(article)

@server.get('/edit_users')
def get_edit_users():
    '''
        get_edit_users
        
        Serves the edit_users page
    '''
    return model.edit_users()

# Searching for user to edit
@server.post('/edit_users')
def post_search_user():
    '''
        post_change_password
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    user = request.forms.get('user')

    # Call the appropriate method
    if request.forms.get("remove") == "Remove user":
        return model.remove_user(user)
    
    # No functionality yet
    if request.forms.get("mute") == "Mute user":
        return model.mute_user(user)
    
    # No functionality yet
    if request.forms.get("mute") == "Unmute user":
        return model.unmute_user(user)
    

# Help with debugging
@server.post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

# 404 errors, use the same trick for other types of errors
@server.error(404)
def error(error): 
    return model.handle_errors(error)

if __name__ == "__main__":

    host = '127.0.0.1'
    port = 8080

    # Turn this off for production
    debug = True

    eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen((host, port)),
                                    certfile='cert.pem',
                                    keyfile='key.pem',
                                    debug=debug,
                                    server_side=True),
                    server.wsgi)
    
    