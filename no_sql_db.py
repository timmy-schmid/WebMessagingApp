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
        self.add_table('users',"username","email", "password", "salt", "public_key", "is_admin", "is_muted")


        '''
            hard coded users
        '''

        import os
        import hashlib
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', "admin1".encode('utf-8'), salt, 100000)
        self.create_table_entry('users', ["Admin", "admin@securechat.com",key, salt,'',True, False])
        self.create_table_entry('users', ["Steven", "steven92@hotmail.com",key, salt,'',False, False])
        self.create_table_entry('users', ["Alice", "alice_is_the_best@yahoo.mail",key, salt,'',False, False])
        self.create_table_entry('users', ["James", "james@techworld.com.au",key, salt,'',False, False])


        '''
            hard coded help articles

        '''
        self.add_table('help_articles',"title", "content")
        self.create_table_entry('help_articles', ["Is the chat system secure?","The chat system is extremely secure! It employs End-to-end encryption (E2EE) to achieve secure communication and does this through the use of WebSockets, sessions and RSA encryption. It's so secure that even our server cannot decipher your messages!"])
        self.create_table_entry('help_articles', ["How do I change my password?","Changing your password is easy! All you have to do is hover over the top right dropdown and then click \"Account Settings\". Once you have reached the account settings page just enter your old password to verify and pick a new one."])
        self.create_table_entry('help_articles', ["How do I report a problem with the platform?","If you have any problems with the platform all you have to do is let Admin know. Once you have logged in, Admin will be within your friends and just message to report any issues."])
        
        '''
            hard coded kx articles

        '''
        self.add_table('knowledge_articles',"title", "content", "author", "anonymous", "comments")

        self.create_table_entry('knowledge_articles', ["Knowledge Repository Rules and Basics","Our knowledge base does not have many rules. We only ask that you be respectful of other students. You can whatever resource, answers, or questions you like, as long as you are respectful of others. Otherwise we will mute you. Happy learning!","Admin", False, []])
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
                                                        "<li>At least 50% total</li></ul>","admin", False, []])
        self.create_table_entry('knowledge_articles', ["Agile Team Roles and Responsibilities","I recently completed a huge project where we worked in Agile teams. For anyone wondering this is the breakdown of the Agile roles." +
                                                        "<h3>Scrum Master or Agile Team Leader</h3>" +
                                                        "Scrum is very specific about the role of a Scrum Master as it is an integral part of the method." +
                                                        "<h4>Key Responsibilities:</h4>"
                                                        "<ul>"+
                                                            "<li>Eliminating Road Blocks – Some blockages encountered by the team will be outside their sphere of control or authority to resolve. It is therefore the responsibility of this role to eliminate the blockage to ensure that team maintains its momentum of achieving the objectives of the iteration.</li>" +
                                                            "<li>Facilitating – This is a key technique for keeping the team progressing toward the end goal</li>" +
                                                            "<li>Enforcing the rules – While Agile is light weight and flexible it still does have rules. The scrum master is responsible for ensuring that all team members know how the Agile Process works.</li>" +
                                                            "<li>Protecting the team – Against any request from outside the team that would prevent the team members from meeting their sprint goal.</li>" +
                                                        "</ul>" +
                                                        "<h3>Product Owner</h3>" +
                                                        "This is the role responsible for working with the customers and stakeholders to determine the requirements and communicate the details of these to the team." +
                                                        "<h4>Key Responsibilities:</h4>"
                                                        "<ul>"+
                                                            "<li>Writing user stories</li>" +
                                                            "<li>Setting the priorities of the stories to be implemented within the iteration to ensure that the most important stories are worked on first</li>" +
                                                            "<li>Being available for the team when they need elaboration on the stories. They use their knowledge to drill-down into what the story needs to do in the system</li>" +
                                                            "<li>Participating in acceptance testing of the stories delivered in each iteration.</li>" +
                                                        "</ul>" +
                                                        "<h3>Development Team</h3>" +
                                                        "The development team consist of professionals who do the work of delivering the product. This comprises of Developers, Testers, Designers, Architects etc as applicable to the project or organizational needs." +
                                                        "<h4>Key Responsibilities:</h4>"
                                                        "<ul>"+
                                                            "<li>Write the code</li>" +
                                                            "<li>Collaborate with product owners and testers to make sure the right code is being written</li>" +
                                                            "<li>Write unit tests</li>" +
                                                            "<li>Checking the code into the version control system for each build</li>" +
                                                        "</ul>"
                                                        ,"Steven", True, []])
        self.create_table_entry('knowledge_articles', ["Help! My assignment won't compile :(","I've been trying to fix it for ages but keep getting this error message:\n"
                                                       "<p>,\"Bob\"])" + \
                                                        "<p>^" + \
                                                        "<p>SyntaxError: invalid syntax" + \
                                                        "<p>Does anyone have any advice?"
                                                        ,"Alice", False, ["Steven: Have you checked that all elements in your array are correct? I've had this happen to me and I had a quotation mark I hadn't closed."]])
        self.create_table_entry('knowledge_articles', ["Algorithms and Datastructure Essentials", "Here is a small table with the key data structures and information on each.\n" +  
                                                       "<h2>Part 1</h2>" + 
                                                       "<table style=\"width:100%\" border=\"1px solid black\">" +
                                                       "<tr>" +
                                                            "<td><h4>Data Structure</h4></td>" + 
                                                            "<td><h4>Lists</h4></td>" + 
                                                            "<td><h4>Trees</h4></td>" + 
                                                            "<td><h4>Binary Search Trees</h4></td>" + 
                                                            "<td><h4>Priority Queue</h4></td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Description</td>" + 
                                                            "<td>A mutable, or changeable, ordered sequence of elements</td>" + 
                                                            "<td>A tree T is made up of a set of nodes endowed with a parent-child relationship</td>" + 
                                                            "<td>for any node v in the tree and any node u in the left subtree of v and any node w in the right subree of v, key(u) < key(v) < key(w)</td>" + 
                                                            "<td>Special type of ADT map to store a collection of key-value items where we can only remove smallest key. Mainly used for sorting </td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Types</td>" + 
                                                            "<td>Array, linked list, stack, queue</td>" + 
                                                            "<td>Tree, binary tree</td>" + 
                                                            "<td>AVL tree, Map (list-based or tree based)</td>" + 
                                                            "<td>Priority queue, heap</td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Other</td>" + 
                                                            "<td></td>" + 
                                                            "<td>Euler traversal (for preorder, inorder, postorder)</td>" + 
                                                            "<td>Trinode restructure</td>" + 
                                                            "<td>Sorting (priority queue sort, selection-sort, insertion-sort, heap sort)</td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Time Complexity (average)</td>" + 
                                                            "<td>O(n)</td>" + 
                                                            "<td>O(n)</td>" + 
                                                            "<td>O(logn)</td>" + 
                                                            "<td>O(logn)</td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Space Complexity (average)</td>" + 
                                                            "<td>O(N) or O(n)</td>" + 
                                                            "<td>O(n)</td>" + 
                                                            "<td>O(n)</td>" + 
                                                            "<td>O(n)</td>" + 
                                                        "</tr>" +
                                                        "</table>" +
                                                        "<h2>Part 2</h2>" + 
                                                        "<table style=\"width:100%\" border=\"1px solid black\">" +
                                                        "<tr>" +
                                                            "<td><h4>Data Structure</h4></td>" + 
                                                            "<td><h4>Hash Tables</h4></td>" + 
                                                            "<td><h4>Graphs</h4></td>" + 
                                                            "<td><h4>Shortest Paths and Minimum Spanning Trees</h4></td>" + 
                                                            "<td><h4>Greedy Method</h4></td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Description</td>" + 
                                                            "<td>Use a hash function h to map keys to corresponding indices in an array A</td>" + 
                                                            "<td>A graph G is a pair (V, E) where V is a set of nodes, called vertices and E is a collection of pairs of vertices, called edges</td>" + 
                                                            "<td>Find a shortest path between two vertices, or the minimum spanning tree of a connected graph</td>" + 
                                                            "<td>We build a solution one step at a time making locally optimal choices at each stage in the hope of finding a global optimum solution</td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Types</td>" + 
                                                            "<td>Separate chaining, linear probing, cuckoo hashing</td>" + 
                                                            "<td>Edge list, adjacency list, adjacency matrix</td>" + 
                                                            "<td>Dijstra's algorithm, Prim's algorithm, Kruskal's algorithn</td>" + 
                                                            "<td></td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Other</td>" + 
                                                            "<td>Load factor alpha (n/N)</td>" + 
                                                            "<td>Graph traversal (BFS, DFS), cut edges</td>" + 
                                                            "<td>Cut property, cycle property, union find, Lexicographic tiebreaking</td>" + 
                                                            "<td>Fractional knapsack, task scheduling, text compression (huffman's algorithm)</td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Time Complexity (average)</td>" + 
                                                            "<td>Best case O(1), but mostly O(1 + alpha)</td>" + 
                                                            "<td>O(1) to insert and remove vertices, O(m) to traverse where m is the number of edges</td>" + 
                                                            "<td>O(mlogn), O(mn) for Kruskal's</td>" + 
                                                            "<td>Depends on the task</td>" + 
                                                        "</tr>" +
                                                        "<tr>" +
                                                            "<td>Space Complexity (average)</td>" + 
                                                            "<td>O(n)</td>" + 
                                                            "<td>O(n + m)</td>" + 
                                                            "<td>Algorithm doesn't take extra space, but the tree is still O(n + m) </td>" + 
                                                            "<td>Depends on the task</td>" + 
                                                        "</tr>" +
                                                        "</table>","Alice", False, ["Admin: Thanks so much Alice, this is great information for everyone to use!", "James: this is such a good summary"]])
        self.create_table_entry('knowledge_articles', ["Does anyone know of any good computing websites for C?","Hey everyone, I'm really struggling with a subject where we are learning C and was wondering if anyone who has learnt C before has any websites they would recommend that helped them?","Alice", False, ["Steven: Yeah I loved initially learning on Codeacademy (https://www.codecademy.com/learn/paths/c) and then W3schools (https://www.w3schools.com/c/index.php) also helped me with extra info on topics I was struggling with"]])
        self.create_table_entry('knowledge_articles', ["CSS Introduction", "Given I've recently used CSS for a lot of assessments I though I would explain what it is and why it is useful." +
                                                       "<h4>What is CSS?</h4>"
                                                        "<ul>"+
                                                            "<li>CSS stands for Cascading Style Sheets</li>" +
                                                            "<li>CSS describes how HTML elements are to be displayed on screen, paper, or in other media</li>" +
                                                            "<li>CSS saves a lot of work. It can control the layout of multiple web pages all at once</li>" +
                                                            "<li>External stylesheets are stored in CSS files</li>" +
                                                        "</ul>" +
                                                        "<h4>Why use CSS?</h4>" +
                                                        "<p>CSS is used to define styles for your web pages, including the design, layout and variations in display for different devices and screen sizes.</p>" +
                                                        "<h4>CSS Solved a Big Problem</h4>" +
                                                        "<p>CSS is used to define styles for your web pages, including the design, layout and variations in display for different devices and screen sizes.</p>" +
                                                        "<p>HTML was NEVER intended to contain tags for formatting a web page!</p>"
                                                        "<p>When tags like font, and color attributes were added to the HTML 3.2 specification, it started a nightmare for web developers. Development of large websites, where fonts and color information were added to every single page, became a long and expensive process. To solve this problem, the World Wide Web Consortium (W3C) created CSS. CSS removed the style formatting from the HTML page!</p>" +
                                                        "<h4>CSS Saves a Lot of Work!</h4>" +
                                                        "<p>The style definitions are normally saved in external .css files. With an external stylesheet file, you can change the look of an entire website by changing just one file!</p>"
                                                        ,"James", False, []])
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
