from pymongo import MongoClient
import dns
from update import Update
from answer import AnswerMethod

class Permission:
    client = None
    db = None
    collection = None
        
    def accept_permission(self, chat_id, accept=True):
        if accept:
            doc = {'chat_id':chat_id, 'role':'user', 'permission':True}
            self.collection.insert_one(doc)
            self.client.close()
            print(f"{chat_id} has changed permission to [USER]")

    def pause_permission(self, chat_id):
        doc = {'chat_id':chat_id, 'role':'stranger', 'permission':False}
        self.collection.insert_one(doc)
        self.client.close()
        print(f"{chat_id} has changed permission to [STRANGER]")

    def permission_list(self):
        a = []
        result = self.collection.find({'permission': True})
        for i in result:
            a.append(i['chat_id'])
        self.client.close()
        return a
    
    def permission_check(self, chat_id):
        result = self.collection.find_one({'permission': True, 'chat_id':chat_id})
        self.client.close()
        if result:
            return result['permission']
        else:
            return False
        
    def stranger_check(self, chat_id):
        result = self.collection.find_one({'role':'stranger', 'chat_id':chat_id})
        self.client.close()
        if result:
            return True
        else:
            return False
    
    def get_admins(self):
        a = []
        result = self.collection.find({'role': 'admin'})
        self.client.close()
        for i in result:
            a.append(i['chat_id'])
        return a

    def get_users(self):
        a = []
        result = self.collection.find({'role': 'user'})
        self.client.close()
        for i in result:
            a.append(i['chat_id'])
        return a

class Login(Permission, Update):


    def __init__(self, bot_url, data):
        self.data = data
        self.start()
        self.BOT_URL = bot_url
        self.client = MongoClient("mongodb+srv://Agiorno:1Qaz2Wsx3Edc!!!@clustertest.g24jd.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.db = self.client.Rada
        self.collection = self.db.BOT
        
        if self.my_type == 'channel_post':
            pass
        elif self.my_type == 'my_chat_member':
            if self.permission_check(self.from_id):
                self.status = True
            else:
                self.leave_chat()
                self.status = False

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


    def json_data(self, chat_id):
        kb = AnswerMethod().make_inline_keyboard(option1 = { "text": "Авторизовать", "callback_data": "1auth" },
                                              option2 = { "text": "Шли на хуй", "callback_data": "2auth" })
        print('К нам стучится левый(ая) хуй')
        json_data = {
            "text": f'К нам стучится {self.chat_id}. Авторизовать?',
            "chat_id" : chat_id,
            "parse_mode": 'markdown',
            'reply_markup': kb
        }      
        return json_data

    def answer(self):
        if self.message == "1auth":
            chat_id = int(self.data['callback_query']['message']['text'].split("К нам стучится ")[1].split('.')[0])
            self.accept_permission(chat_id)
            js = {
                'text':'Вы успешно авторизованы. Напишите номер законопроекта, который вас интересует.',
                'chat_id':chat_id
            }
            self.send_message(self.just_text('Новый пользователь добавлен успешно'))
            self.send_message(js)
            print(self.get_users())
        # отказались
        else:
            self.send_message(self.just_text('Клиент послан на хуй. Успешно, конечно, что за вопросы?!'))
            chat_id = int(self.data['callback_query']['message']['text'].split("К нам стучится ")[1].split('.')[0])
            self.pause_permission(chat_id)

        
        # после чего удаляем клавиатуру
        self.edit_reply(self.message_id, 172185928)
        self.edit_reply(int(self.message_id)-1, 114660111)
        print('[ЛОГИН]: КЛАВИАТУРА УДАЛЕНА')
            


                
