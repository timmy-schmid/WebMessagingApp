
## Notes ##

### Progress Tim 12/04 ##

Hi Allanah. I had a big day of research and working on our code with many ups and downs. Here's a summary of what I achieved and learnts.

- Sockets: Today I found out there is a big difference between [sockets and WebSockets](https://stackoverflow.com/questions/4973622/difference-between-socket-and-websocket), most Python web frameworks have a way of implementing them and this usually involves [Socket.io](https://socket.io/). I decided to stick with the current template over migrating to Winston's that uses Flask. Bottle is more than capable of implementing WebSockets and I found some tutorials/example projects to help me achieve this through the Socket.io library [Here is one](https://github.com/miguelgrinberg/python-socketio/blob/main/examples/server/wsgi/app.py). Python . You will need to use the command `pip install python-socketio` to get this to work. The official socket.io python api documentation can be found [here](https://python-socketio.readthedocs.io/en/latest/server.html#deployment-strategies)

- Bottle: I decided to skim through the bottle documentation to get a good understanding to what is capable including using web cookies (discussed later), I found the [official documentation](https://bottlepy.org/docs/stable/tutorial.html#) extremely useful

- Views: The current way that views in our project was setup was to render using python String Templates, I found this quite restrictive and it results in many .html files. I was planning to change this to Jinja2, however I realised Bottle has a built in rendering engine called [SimpleTemplate](https://bottlepy.org/docs/dev/stpl.html#bottle.SimpleTemplate). What this allows us to do is to use pythonic code directly in our html files, and in turn lets us create dynamic pages/views. I've flattened all our templates into just a couple of files now using if statements to determine what to display based on the user's login status.

-Sessions: A big thing that I was trying to figure out is how we know if a user is 'logged in' or not. Yes, we were doing the authentication of the user against our temporal database however after this (or before this) we didn't do any checks. This meant that we could access any of the pages just by typing the URL's in directly which was not great from a security perspective. I also needed to figure out a way to how to determine a chat window unique to that user. I found that typically a *session* is generated between the server and the client and is typically stored via web cookies. I got a bit lost on how to do this so I looked up the Bottle documentation and found [this video](https://www.youtube.com/watch?v=l66XCSaeTys). Essentially a unique uid code is created when a user logs in which is added to a sessions dictionary on the server side. The server then checks to see if a clients cookie matches an active session whenever it accesses parts of the website. This is done in the model function `get_session_username()`.

-Create User, Login: I refactored these a bit and fixed some logic errors. I also added some basic checks like if the create user form was being submitted with blank data, if the password is the same as the username etc.

-Friends and Chat: I changed friends to only display all users, except the current one logged in. I also added links to each friend which includes GET information (in the URL) about the friend. I've implemented a basic chat window for now. I know that we decided that you would do this, but after revisiting I believe it was necessary to get this setup for sockets to work.

Tomorrow I'm going to tackle implementing secure sockets. I actually believe this shoudn't take to long now since I have a good idea of what needs to be done. There's a few video's [here](https://www.youtube.com/watch?v=U_Q1vqaJi34)
[here](https://www.youtube.com/watch?v=whEObh8waxg) that I've skimmed through. There's also Winston's template to look through as he also uses Socket.IO. Feel free to also have a go at this.

In terms of other things that can be done there's a few things I've listed in the worddoc that we could still implement to help us strenghten the other sections of the project. I.e. it would be good to implement some type of regex to require a user to enter certain charcters for the password. Also it could be good to maybe try to have a limit on the number of attempts a user can incorrectly enter a password before it locks them out.

### Progress Alannah 3/04 ##
I got the certificate to be trusted!

I saw something on Ed about including the IP in the certificate [this] (https://edstem.org/au/courses/10797/discussion/1267056) and the looked it up and found [this](https://medium.com/@antelle/how-to-generate-a-self-signed-ssl-certificate-for-an-ip-address-f0dd8dddf754). I followed it and it worked! I also added the certificate to my keychain and made it trust it, which I think you will have to do too. 

The new certificate is in the 'trust_certificate' branch so if you run the server from there it should work. If it does then we can merge the branch into main, but if it doesn't we can trouble shoot more.


### Progress Alannah 26/03 ###
Hey Tim, after failing to get my computer to trust the certificate last night, I just quickly did some very basic database setup on the new "users" branch which we can merge in when more progress has been made. I setup the very basic database found in their "no_sql_db.py" to play around with getting that working. I haven't used SQL before, but if you have I'm more than happy to transfer that over to the SQL database. Anyway, you can now login as either user a or b which have very secure user info (not):
  username: a
  password: password
  
  username: b
  password: password
 
 I guess the next step here would be storing the passwords properly/safely.

### Progress Tim 24/03 ###

Hi Alannah, here's what I got up to last night:

- I followed the guide [here](https://deliciousbrains.com/ssl-certificate-authority-for-local-https-development/) from last weeks tutorial to setup a CA and our own private key to create a signed certificate. You can find the files that were generated in the cert folder, as well as localhost.cert and localhost.crt copied to the parent folder which is used by our program. I also added the certificate to my local machines trusted cert list on Windows, you'll need to do this step for your computer as well.

- Bottle does not support SSL out of the box, you need a 3rd party library. I tried a bunch and kept on running into issues with dependencies not being compatible with Windows OS. After trying to come up with a work around and realising I was spending way to much time on it I eventually moved over to running the server through a VirtualBox.

  - I started with Cheeroot library for SSL, and built my own adapter for it to work with bottle [based off this person](https://github.com/nickbabcock/bottle-ssl) but I failed to get it to load a page properly, probably to do with how the template configured. I then moved to gunicorn which works out of the box.  You can install this using pip ```install gunicorn``` on your computer. To get this to work all I needed to do was specify the server was gunicorn and add the private key and certificate filenames into the server run function.

- So after spinning up the server it was able to load as an HTTPS site in all browsers however it lets of an 'unsecure' warning. I thought that adding the certifate to my machines trusted list would have worked but no dice. I tried a bunch of different things with help from [this](https://stackoverflow.com/questions/30977264/subject-alternative-name-not-present-in-certificate/47779814#47779814) and [this](https://stackoverflow.com/questions/7580508/getting-chrome-to-accept-self-signed-localhost-certificate) stackoverflow, including regenerating the CA and cert files with different settings, but I could not get the browser to trust the certificate. I gave up as it was getting late. I'd be interested to see if you can get browsers to trust this on Mac.
  - Also as a side - I'm not sure if it's a requirement for us to get the browsers to 'trust' the CA and certificate for the assignment or just get HTTPS to work (which from my understanding it does). It would be good to get clarification from Daniel on Monday

Anyway, hope this helps.

## Overview ##

This template has been roughly set up around a 'Model View Controller' or MVC design. This splits the functions of your site into three distinct categories:

- Models: Handles the program logic
- Views: Handles the returned HTML pages
- Controllers: Handles the requests for pages that the user sends

Typically the user will request a page (from the controller), the request will be interpreted and then passed to the program logic (the model) which will generate a new page to return to the user (the view).


This setup has been used to keep the logic of the code and the logic of the site separate. 


If your site starts sprawling enough, you may wish to create distinct folders for each of these categories and then split the code into separate files within these folders.

## Controllers ##

This is the handler for your server requests. Your get and post decorators will go here, before calling a model to handle any actual lifting.

All of your bottle relevant code should live here. The rest of your code should not be exposed to anything to do with bottle. Similarly, no SQL or other 'database' or logical code should live up here. You have been provided with static file loads for javascript, css and image files from the javascript, css and img directories respectively.


## Models ##

The brains of the operation, here we perform whatever actual code we need, before calling our view object to return the templated HTML. This area should make calls to any 'databases' or other persistent storage that is handling user or other data.


## HTTPS ##
The library bottle used in the template does not support ssl. To enable bottle server in the template support https/ssl in python, one python library of WSGI that Bottle supports is needed. There are many choices, such as Gunicorn, CherryPy, etc. If you are still unclear, just google sth like how to enable Bottle server support HTTPS python. It is definitely fine if you use some libraries other than Bottle.





## Views ##

Simply loads our HTML files and renders any elements of the template.

It might be helpful to have an explanation of the View class. You do not actually need this to use bottle at all, but it's a primitive method of automating loading and rendering HTML templates.If you already have your own method of managing this, please feel free to disregard the explanation below. If you don't like how parts of this have been implemented, you are more than free to modify it for your own use.

The template has been modified to be more explicit and verbose in what it is doing rather than strictly the most efficient or Pythonesque method. 

If you're completely lost: the point of this code is to "render HTML", all this really means is that we're going to take a string, modify it a bit and return it. HTML is effectively just some specially formatted text. I would suggest starting by looking at and building the polling site in tutorial 3. 

All the code below is just to read text from a file, replace a few keywords and then return it. 

Once you've completed the polling site you might wonder if hard coding all the HTML responses is the most efficient method. Depending on the size of the project it might or it might not be. It is entirely possible to hard code all the pages required for this assignment. However, one method of managing HTML is to store it in a separate file, then read and return it when required.  

This is performed by the load_template method. It opens a file given by the filename argument that is found at the filename path (here it's "/template") and with the template extension (here it's ".html").

```python
def load_template(self, filename):
        path = self.template_path + filename + self.template_extension
        file = open(path, 'r')
        text = ""
        for line in file:
            text += line
        file.close()
        return text
```

Of course some times you want dynamically generated HTML (for example, displaying a username after logging in). In order to do this we're going to need to do some string operations.

```python
def string_format(string, format_dict):
    for keyword in format_dict:
        string = string.replace('{' + keyword + '}', format_dict[keyword])
    return string

string = "Thanks for logging in {user}."
format_dict = {"user":"Anon"}
formatted_string = string_format(string, format_dict)
print(formatted_string)
```

Or instead we can use the Python format function:

```python
string = "My hovercraft is full of {things}"
formatted_string = string.format(things="eels")
print(formatted_string)
```

The simple_render method within View calls the Python safe_substitute function on a given template, this works in a very similar fashion to the format function we saw previously.


```python
def simple_render(self, template, **kwargs):
        template = string.Template(template)
        template = template.safe_substitute(**kwargs)
        return  template
```

\*\*kwargs is a Python default method of passing arbitrary keyword arguments (see tutorial 1!) as a dictionary, this lets us pass our dictionary around without actually having to worry about the contents.

Now let's say that there are some "global" dynamic template options we want to use, things that we can just pass into a template when it's called. For this we'll follow exactly the same method as above, but store these "global renders" as a member variable. 

```python
def __init__(self, 
        template_path="templates/", 
        template_extension=".html", 
        **kwargs):
        self.template_path = template_path
        self.template_extension = template_extension
        self.global_renders = kwargs
```
Here we're using \*\*kwargs again for the "global renders"...

```python
def render(self, template, **kwargs):
         ''' 
            render
            A more complex render that joins global settings with local settings

            :: template :: The template to use
            :: kwargs :: The local key value pairs to pass to the template
        '''
        # Construct the head, body and tail separately
        rendered_body = self.simple_render(body_template, **kwargs)
        rendered_head = self.simple_render(header_template, **kwargs)
        rendered_tail = self.simple_render(tailer_template, **kwargs)

        # Join them
        rendered_template = rendered_head + rendered_body + rendered_tail

        # Apply any global templating that needs to occur
        rendered_template = self.global_render(rendered_template)

        # Return the template
        return rendered_template

```
...and here we build the header, tailer and body, join them together and then apply any global replacements we might need 

Lastly let's consider some generic headers we can add to every page on the site (in the case of Drawing Straws, this is the menu bar and the image on every page), and the "tailer" to properly enclose the HTML. This can be more efficiently managed using  proper rendering calls but this template was not built for flexibility so much as for ease of use on a few small sites.

Putting it all together we now get our load and render method:
```python
def load_and_render(self, filename, header="header", tailer="tailer", **kwargs):
        ''' 
            Loads and renders templates

            :: filename :: Name of the template to load
            :: header :: Header template to use, swap this out for multiple headers 
            :: tailer :: Tailer template to use
            :: kwargs :: Keyword arguments to pass
        '''
        body_template = self.load_template(filename)
        header_template = self.load_template(header)
        tailer_template = self.load_template(tailer)

        rendered_template = self.render(
            body_template=body_template, 
            header_template=header_template, 
            tailer_template=tailer_template, 
            **kwargs)

        return rendered_template
```
And that's the View class. It's quite a simple template framework compared to some of the more featured ones used in larger scale web development, but it provides the basic features required for this assignment.

If you are confused about all this I would suggest loading up the template site and looking at the "about" page. Modify the garble keyword on the line:

```python
return view("about", garble=np.random.choice(garble))
```
To something like:

```python
return view("about", garble="My String!")
```

Then reload the site and have a look at the "about" page. Have a look at the "{garble}" section of the "about.html" file in the templates directory.

I

## SQL ##
Not strictly a requirement, if you want to use SQLite3 then some sample code has been provided in the SQL file. This code is not necessarily in a fully working state, and you will probably want to modify it extensively.
If you are unsure why something is working in a particular way, be sure to read all the comments before making an Ed post.


## Javascript ##
Also not strictly a requirement, if you wish to use javascript it **must** be loaded locally, CDNs and loading from external sites is prohibited.


## End notes ##

I hope this helps explain what's going on. If you're still unsure about all of this please ask sooner rather than later.
