'''
    This is a file that configures how your server runs
    You may eventually wish to have your own explicit config file
    that this reads from.
'''

import sys
import eventlet
from bottle import run, Bottle

#-----------------------------------------------------------------------------
# You may eventually wish to put these in their own directories and then load 
# Each file separately

# For the template, we will keep them together
import model
import view
from controller import server
#-----------------------------------------------------------------------------

# It might be a good idea to move the following settings to a config file and then load them
# Change this to your IP address or 0.0.0.0 when actually hosting
host = ''
port = 8080

# Turn this off for production
debug = True

app = Bottle()
app.merge(server)

def run_server():
    eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen((host, port)),
                                       certfile='cert.pem',
                                       keyfile='key.pem',
                                       debug=debug,
                                       server_side=True),
                    app.wsgi)



# Optional SQL support
"""
def manage_db():
    '''
        Blank function for database support, use as needed
    '''


import sql
    
def manage_db():
    '''
        manage_db
        Starts up and re-initialises an SQL databse for the server
    '''
    database_args = ":memory:" # Currently runs in RAM, might want to change this to a file if you use it
    sql_db = sql.SQLDatabase(database_args=database_args)

    return
"""

def run_commands(args):
    '''
        run_commands
        Parses arguments as commands and runs them if they match the command list

        :: args :: Command line arguments passed to this function
    '''
    commands = args[1:]

    # Default command
    if len(commands) == 0:
        commands = [default_command]

    for command in commands:
        if command in command_list:
            command_list[command]()
        else:
            print("Command '{command}' not found".format(command=command))

if __name__ == "__main__":
    # What commands can be run with this python file
    # Add your own here as you see fit
    command_list = {
        #'manage_db' : manage_db,
        'server'       : run_server
    }

    # The default command if none other is given
    default_command = 'server'

    #manage_db()
    run_commands(sys.argv)