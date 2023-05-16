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
        return [[val[self.fields.index(target_field_name)]] for val in self.entries]
    

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
