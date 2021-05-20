from pymongo import MongoClient
import requests
import ast

with open("monkey", "r") as f:
    bot = ast.literal_eval(f.read())

class User():
    client = MongoClient(bot['mongo'])
    db = client.Rada
    log = db.Log
    users = db.BOT

    def currentScope(self):
        self.user = self.users.find_one({'chat_id':self.chat_id})
        print(f'self.user == {self.user}')
        try:
           self.scope =  self.user['scope']
        except:
            _filter = {'chat_id':self.chat_id}
            value = { "$set": { 'scope': 'general' } }
            self.db.BOT.update_one(_filter, value)
            self.scope = 'general'
        return self.scope

    def changeScope(self, name):
        self.user = self.users.find_one({'chat_id':self.chat_id})
        _filter = {'chat_id':self.chat_id}
        value = { "$set": { 'scope': name} }
        self.db.BOT.update_one(_filter, value)
        self.scope = name
    
    def getTags(self):
        self.user = self.users.find_one({'chat_id':self.chat_id})
        try:
            self.tags = self.user['tags']
        except:
            _filter = {'chat_id':self.chat_id}
            value = { "$set": { 'tags': [] } }
            self.db.BOT.update_one(_filter, value)
            self.tags = []
        return self.tags
    
    def createTags(self, name, value=None):
        if not value:
            value = []
        _filter = {'chat_id':self.chat_id}
        value = { "$set": { 'tags': [{name: value}] } }
        self.db.BOT.update_one(_filter, value)
    
    def choose_tags(self, name):
        try:
            for i in self.tags:
                if name in i.keys():
                    position = self.tags.index(i)
            my_tags = self.tags[position][name]
        except:
            my_tags = []
        return my_tags

    def existing_tags(self):
        t = []
        for i in self.tags:
            t.append(list(i.keys())[0])
        return t

    def edit_tags(self, name, old_values, new_values):
        n = f'tags.{name}'
        n1 = f'tags.$.{name}'
        _filter = {'chat_id':self.chat_id, n:old_values}
        value = {'$addToSet':{n1:{'$each': new_values}}}
        self.db.BOT.update_one(_filter, value)

    def remove_tags(self, name, old_values, values):
        n = f'tags.{name}'
        n1 = f'tags.$.{name}'
        _filter = {'chat_id':self.chat_id, n:old_values}
        val = {'$pullAll':{n1:values}}
        self.db.BOT.update_one(_filter, val)

    def remove_all(self, name, old_values):
        n = f'tags.{name}'
        _filter = {'chat_id':self.chat_id, n:old_values}
        val = {'$pull':{'tags':{name:old_values}}}
        self.db.BOT.update_one(_filter, val)

    def new_set(self, name, values):
        _filter = {'chat_id':self.chat_id}
        value = {'$addToSet':{'tags':{name: values}}}
        self.db.BOT.update_one(_filter, value)

    def options(self):
        self.user = self.users.find_one({'chat_id':self.chat_id})
        try:
            self.option = self.user['options']
        except:
            _filter = {'chat_id':self.chat_id}
            value = { "$set": { 'options': { 'CRM': False } } }
            self.db.BOT.update_one(_filter, value)
            self.option = { 'CRM': False } 
        return self.option



        

