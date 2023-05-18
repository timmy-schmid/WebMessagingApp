# This file provides a very simple "no sql database using python dictionaries"
# If you don't know SQL then you might consider something like this for this course
# We're not using a class here as we're roughly expecting this to be a singleton

# If you need to multithread this, a cheap and easy way is to stick it on its own bottle server on a different port
# Write a few dispatch methods and add routes

# A heads up, this code is for demonstration purposes; you might want to modify it for your own needs
# Currently it does basic insertions and lookups

class Table():
    def __init__(self, table_name, *table_fields):
        self.entries = []
        self.fields = table_fields
        self.name = table_name

    def create_entry(self, data):
        '''
        Inserts an entry in the table
        Doesn't do any type checking
        '''

        # Bare minimum, we'll check the number of fields
        if len(data) != len(self.fields):
            raise ValueError('Wrong number of fields for table')

        self.entries.append(data)
        return
    
    def remove_entry(self, data):
        '''
        Inserts an entry in the table
        Doesn't do any type checking
        '''

        # Bare minimum, we'll check the number of fields
        if len(data) != len(self.fields):
            raise ValueError('Wrong number of fields for table')

        self.entries.remove(data)
        return

    def search_table_for_entry(self, target_field_name, target_value):
        '''
            Search the table given a field name and a target value
            Returns the first entry found that matches
        '''
        # Lazy search for matching entries
        for entry in self.entries:
            for field_name, value in zip(self.fields, entry):
                if target_field_name == field_name and target_value == value:
                    return entry

        # Nothing Found
        return None
    
    def search_table_for_value(self, target_field_name, target_value, index):
        '''
            Search the table given a field name and a target value
            Returns the first entry found that matches
        '''
        # Lazy search for matching entries
        for entry in self.entries:
            for field_name, value in zip(self.fields, entry):
                if target_field_name == field_name and target_value == value:
                    return entry[index]

        # Nothing Found
        return None
    
    def select_all_table_values(self,target_field_name):
        return [val[self.fields.index(target_field_name)] for val in self.entries]
    

    #returns the number of fields updated
    def update_table_val(self, search_field, search_val, set_field, set_value):

        count = 0
        for entry in self.entries:
            for field_name, value in zip(self.fields, entry):
                if search_field == field_name and search_val == value:
                    entry[self.fields.index(set_field)] = set_value      
                    count +=1
        return count

class DB():
    '''
    This is a singleton class that handles all the tables
    You'll probably want to extend this with features like multiple lookups, and deletion
    A method to write to and load from file might also be useful for your purposes
    '''
    def __init__(self):
        self.tables = {}

        # Setup your tables
        self.add_table('users',"username", "password", "salt",'public_key', 'is_admin')


        '''
            hard coded users
        '''

        import os
        import hashlib
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', "admin1".encode('utf-8'), salt, 100000)
        self.create_table_entry('users', ["Steven",key,salt,'',False])
        self.create_table_entry('users', ["Alice",key,salt,'',False])
        self.create_table_entry('users', ["James",key,salt,'',False])


        '''
            hard coded help articles

        '''
        self.add_table('help_articles',"title", "content")
        self.create_table_entry('help_articles', ["Is the chat system secure?","chat system Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus."])
        self.create_table_entry('help_articles', ["How do I change my password?"," password Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus."])
        self.create_table_entry('help_articles', ["How do I use a screenreader for accessibility?","screenreader Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus."])
        
        '''
            hard coded kx articles

        '''
        self.add_table('knowledge_articles',"title", "content", "author")

        self.create_table_entry('knowledge_articles', ["INFO2222 Courseguide",
                                                       "<h4>Overview</h4>" + \
                                                        "<p>This unit provides an integrated treatment of two critical topics for a computing professional: human computer interaction (HCI) and security. The techniques and core ideas of HCI will be studied with a particular focus on examples and case studies related to security. This unit builds the students' awareness of the deep challenges in creating computing systems that can meet people's needs for both HCI and security. It will develop basic skills to evaluate systems for their effectiveness in meeting people's needs within the contexts of their use, building knowledge of common mistakes in systems, and approaches to avoid those mistakes.</p>" + \
                                                        "<h4>Project</h4>" + \
                                                        "<p>Students work in a team to design and develop a ‘usable and secure’ website, with an End-to-End encrypted secure messaging function. Each student will be required to review their own performance and that of each team members and explain them (e.g., contribution portion, or which specific checking points) in the project reports. Individual marks for group assessments will be determined by the overall group product as well as the individual contributions.</p>" + \
                                                        "<h4>Homeworks</h4>" + \
                                                        "<p>Students work individually, each HW contains several questions to be answered.</p>" + \
                                                        "<h4>Final Exam</h4>" + \
                                                        "<p>Open book online exam that assesses all contents covered in the semester. Students must score at least 40% in the final exam to pass the unit (see Pass requirements). Detailed information for each assessment can be found on Canvas.</p>" + \
                                                        "<p>Conditions for pass in this unit:</p>" + \
                                                        "<ul><li>At least 40% in the progressive marks</li>" + \
                                                        "<li>At least 40% in the final exam</li>" + \
                                                        "<li>At least 50% total</li></ul>","admin"])
        self.create_table_entry('knowledge_articles', ["The History of Cybersecurity","chat system Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus.","Steven"])
        self.create_table_entry('knowledge_articles', ["Algorithms and Datastructure Essentials"," password Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus.","Alice"])
        self.create_table_entry('knowledge_articles', ["How to create Custom CSS Forms","screenreader Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus.","James"])
        self.create_table_entry('knowledge_articles', ["Python 101","chat system Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus.","James"])
        self.create_table_entry('knowledge_articles', ["Help! My assignment won't compile :("," password Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus.","Alice"])
        self.create_table_entry('knowledge_articles', ["Does anyone know of any good computing tutors?","screenreader Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus.","Alice"])
        self.create_table_entry('knowledge_articles', ["Knowledge Repository Rules and Basics","screenreader Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis aliquet magna id quam ultricies semper. Proin quis maximus eros, ac finibus metus. Nulla facilisi. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi ultricies non urna sit amet rutrum. Sed viverra orci ac sem lacinia accumsan. Vestibulum nisl neque, placerat eu leo vel, varius laoreet elit. Aenean imperdiet est nisi, eget rutrum diam vehicula non. Quisque quis tincidunt libero, quis ornare enim. Quisque at placerat ante. Donec non ornare ligula, sit amet convallis orci. Integer euismod pulvinar sapien congue scelerisque. Mauris accumsan dictum magna, auctor ullamcorper mi ultricies quis. Aenean et sodales tortor, eu pretium metus.","Admin"])
        return

    def add_table(self, table_name, *table_fields):
        '''
            Adds a table to the database
        '''
        table = Table(table_name, *table_fields)
        self.tables[table_name] = table

        return
    
    def update_table_val(self, table_name, search_field, search_val, set_field, set_value):
        return self.tables[table_name].update_table_val(search_field,search_val,set_field, set_value)

    def search_table_for_entry(self, table_name, target_field_name, target_value):
        '''
            Calls the search table method on an appropriate table
        '''
        return self.tables[table_name].search_table_for_entry(target_field_name, target_value)
    
    def select_all_table_values(self, table_name,target_field_name):
        return self.tables[table_name].select_all_table_values(target_field_name)


    def search_table_for_value(self, table_name, target_field_name, target_value, index):
        '''
            Calls the search table method on an appropriate table
        '''
        return self.tables[table_name].search_table_for_value(target_field_name, target_value, index)

    def create_table_entry(self, table_name, data):
        '''
            Calls the create entry method on the appropriate table
        '''
        return self.tables[table_name].create_entry(data)
    
    def remove_table_entry(self, table_name, data):
        '''
            Calls the create entry method on the appropriate table
        '''
        return self.tables[table_name].remove_entry(data)


# Our global database
# Invoke this as needed
database = DB()
