from pymongo import MongoClient
import dns
from update import Update
from answer import AnswerMethod
import ast

with open("monkey", "r") as f:
    bot = ast.literal_eval(f.read())

class Permission:
    client = None
    db = None
    users = None
    collection = None
        
    def accept_permission(self, chat_id,is_bot, first_name, last_name, user_name):
        doc = {'chat_id':chat_id, 'first_name': first_name, 'last_name': last_name, 'user_name':user_name, 'is_bot':is_bot, 'role':'user', 'permission':True, 'tags':[]}
        self.users.insert_one(doc)
        self.client.close()
        print(f"{chat_id} has changed permission to [USER]")

    def pause_permission(self, chat_id, is_bot, first_name, last_name, user_name):
        doc = {'chat_id':chat_id, 'first_name': first_name, 'last_name': last_name, 'user_name':user_name, 'is_bot':is_bot, 'role':'user', 'permission':True, 'tags':[]}
        self.users.insert_one(doc)
        self.client.close()
        print(f"{chat_id} has changed permission to [STRANGER]")

    def permission_list(self):
        a = []
        result = self.users.find({'permission': True})
        for i in result:
            a.append(i['chat_id'])
        self.client.close()
        return a
    
    def permission_check(self, chat_id):
        result = self.users.find_one({'permission': True, 'chat_id':chat_id})
        self.client.close()
        if result:
            return result['permission']
        else:
            return False
        
    def stranger_check(self, chat_id):
        result = self.users.find_one({'role':'stranger', 'chat_id':chat_id})
        self.client.close()
        if result:
            return True
        else:
            return False
    
    def get_admins(self):
        a = []
        admins = self.db.BOT
        result = self.users.find({'role': 'admin'})
        self.client.close()
        for i in result:
            a.append(i['chat_id'])
        return a

    def get_users(self):
        a = []
        result = self.users.find({'role': 'user'})
        self.client.close()
        for i in result:
            a.append(i['chat_id'])
        return a
    


class Login(Permission, Update):
    client = MongoClient(bot['mongo'])
    db = client.Rada
    collection = db.Log
    users = db.BOT

    def __init__(self, bot_url, data):
        self.data = data
        self.BOT_URL = bot_url
        self.send_log_mongo(data)
        self.data.pop('_id')
        self.start()
        
        if self.my_type == 'message':

            if self.permission_check(self.chat_id):
                self.status = True

            elif self.stranger_check(self.chat_id):
                self.send_message(self.just_text('Запрос на авторизацию получен. Ожидайте.'))
                self.status = False

            else:
                self.send_message(self.just_text('Запрос на авторизацию получен. Ожидайте.'))
                for i in self.get_admins():
                    self.send_message(self.json_data(i))
                    print(f"{self.message_id} -- {i}")
                self.status = False
        
        elif self.my_type == 'channel_post':
            self.status = True

        elif self.my_type == 'callback_query':
            self.status = True

        elif self.my_type == 'my_chat_member':
            if self.permission_check(self.from_id):
                self.status = True
            else:
                self.leave_chat()
                self.status = False
        else:
            self.status = False


    def json_data(self, chat_id):
        kb = AnswerMethod().make_inline_keyboard(option1 = { "text": "Авторизовать", "callback_data": "1auth" },
                                              option2 = { "text": "Шли на хуй", "callback_data": "2auth" })
        print('К нам стучится левый(ая) хуй')
        json_data = {
            "text": f'К нам стучится {self.chat_id}. Авторизовать? {self.update_id}',
            "chat_id" : chat_id,
            "parse_mode": 'markdown',
            'reply_markup': kb
        }      
        return json_data

    def simple_json(self, chat_id=None, text = None):
        json_data = {
            'text': text,
            'chat_id': chat_id,
            'parse_mode': 'markdown'
        }
        return json_data

    def answer(self):
        if self.message == "1auth":
            chat_id = int(self.data['callback_query']['message']['text'].split("К нам стучится ")[1].split('.')[0])
            upd_id = int(self.data['callback_query']['message']['text'].split("Авторизовать? ")[1])
            print(upd_id)
            is_bot, first_name, last_name, user_name = self.get_from_update_id(upd_id)
            self.accept_permission(chat_id, is_bot, first_name, last_name, user_name)
            js = {
                'text':'Вы успешно авторизованы. Напишите номер законопроекта, который вас интересует.',
                'chat_id':chat_id
            }
            for i in self.get_admins():
                self.send_message(self.simple_json(text = f'Новый пользователь {first_name} {last_name} добавлен успешно', chat_id=i))
            self.send_message(js)
            print(self.get_users())
        # отказались
        else:
            for i in self.get_admins():
                self.send_message(self.simple_json(text=f'Новый пользователь {first_name} {last_name} послан на хуй', chat_id=i))
            upd_id = int(self.data['callback_query']['message']['text'].split("Авторизовать? ")[1])
            chat_id = int(self.data['callback_query']['message']['text'].split("К нам стучится ")[1].split('.')[0])
            is_bot, first_name, last_name, user_name = self.get_from_update_id(upd_id)
            self.pause_permission(chat_id, is_bot, first_name, last_name, user_name)

        
        # после чего удаляем клавиатуру
        self.edit_reply(self.message_id, 172185928)
        self.edit_reply(int(self.message_id)-1, 114660111)
        print('[ЛОГИН]: КЛАВИАТУРА УДАЛЕНА')
        
    def send_log_mongo(self, data):
        self.collection.insert_one(data)

    def get_from_update_id(self, update_id):
        result = self.collection.find_one({'update_id': update_id})
        print(result)
        try:
            is_bot = result['message']['from']['is_bot']
        except:
            is_bot = None
        try:
            first_name = result['message']['from']['first_name']
        except:
            first_name = None
        try:
            last_name = result['message']['from']['last_name']
        except:
            last_name = None
        try:
            user_name = result['message']['from']['user_name']
        except:
            user_name = None
        return is_bot, first_name, last_name, user_name
