import ast
from pymongo import MongoClient
import requests
from update import Update
from answer import AnswerMethod
import json
from users import User
from collections import defaultdict

with open("monkey", "r") as f:
    bot = ast.literal_eval(f.read())

def dialog():
    print(1)
    u = User()
    print(2)
    u.chat_id = list(Tags.handlers.keys())[-1]
    print(3)    
    print(list(Tags.handlers.keys())[-1])
    print(4)
    print(u.chat_id)
    print(5)
    u.changeScope('/tags')
    print(6)
    print(f'=0 : {check_tags()}')
    print(7)
    if check_tags():
        print(8)
        start = yield from user_has_no_tag(
            '''Набор тегів - це список ключових слів, по яким я можу сказати є вони в законопроекті чи немає.
Дуже корисна річ для моніторингу та аналізу.
Краще поєднувати теги в набори за певною ознакою, наприклад *Корпоративне Управління*.
Давайте створимо ваш перший набір тегів. Як ми будемо його називати?'''
        )
        print(9)
    else:
        start = yield from user_has_tags('У вас вже є набори тегів.')
        print(start)
        print(10)

    

def user_has_no_tag(name):
    tag_name = yield name
    tags = yield f"Чудово! Набір {tag_name} створено! Тепер треба додати самі ключові слова. Напишіть їх через кому. (Наприклад: газ, нафта, рента)"  
    values = tags.lower().strip().split(',')
    u = User()
    u.chat_id = list(Tags.handlers.keys())[-1]
    u.createTags(tag_name.lower().strip(), values)
    u.changeScope('general')
    finish = yield f"Супер! Тепер при аналізі законопроекту я буду шукати в ньому ці ключові слова: {tags}. Зараз можете спробувати ввести номер будь-якого законопроекту, наприклад 1122"

def add_new_set(name):
    tag_name = yield name
    tags = yield f"Чудово! Набір {tag_name} створено! Тепер треба додати самі ключові слова. Напишіть їх через кому. (Наприклад: газ, нафта, рента)"  
    values = tags.lower().strip().split(',')
    u = User()
    u.chat_id = list(Tags.handlers.keys())[-1]
    u.new_set(tag_name.lower().strip(), values)
    u.changeScope('general')
    finish = yield f"Супер! Зараз можете спробувати ввести номер будь-якого законопроекту, наприклад 1122"

def user_has_tags(answer):
    a = yield answer
    print(11)
    u = User()
    print(12)
    u.chat_id = list(Tags.handlers.keys())[-1]
    print(13)
    if a == "1choise_tag":
        print(14)
        start = yield from add_new_set('Добре, зараз створимо новий набір. Яка буде його назва?')
        print(15)
    elif a == "2choise_tag":
        print(16)
        u.getTags()
        print(17)
        tags = u.existing_tags()
        print(18)
        start = yield from update_tags(f'Який з цих наборів ви хочете редагувати {tags}? Просто напишіть назву!')
        print(19)
    elif a == "3choise_tag":
        print(20)
        u.changeScope('general')
        print(21)
        finish = yield 'Без проблем :)'
        print(22)

def update_tags(name):
    tag_name = yield name
    print(f'tag_name = {tag_name}')
    u = User()
    u.chat_id = list(Tags.handlers.keys())[-1]
    u.getTags()
    tags = u.choose_tags(tag_name.lower().strip())
    print(f'tags = {tags}')
    while len(tags) == 0:
        new_name = yield "Набора з такою назвою не існує. Повторіть або напишіть ВИХІД"
        if new_name.lower().strip() == 'вихід':
            u.changeScope('general')
            finish = yield 'Наступного разу вийде краще ))'
            break
        else:
            tag_name = new_name
            tags = u.choose_tags(tag_name.lower().strip())
    question = yield from add_or_remove_tag(f'Зараз в цьому наборі такі ключові слова: {tags}', tag_name, tags)
    
    
def add_or_remove_tag(question, tag_name, tags):
    quest = yield question
    if quest == "1edit_tag":
        tas = yield f"Чудово! Тепер треба додати самі ключові слова. Напишіть їх через кому. (Наприклад: газ, нафта, рента)"  
        new_values = tas.lower().split(',')
        u = User()
        u.chat_id = list(Tags.handlers.keys())[-1]
        print(f'tag_name = {tag_name}, old_values = {tags}, new_values = {new_values}')
        u.edit_tags(tag_name.lower().strip(), tags, new_values)
        u.changeScope('general')
        finish = yield f"Супер! Тепер при аналізі законопроекту я буду шукати в ньому ці ключові слова: {u.choose_tags(tag_name)}. Зараз можете спробувати ввести номер будь-якого законопроекту, наприклад 1122"

    elif quest == "2edit_tag":
        tas = yield f"Ого! Тепер треба написати зайві ключові слова. Напишіть їх через кому. (Наприклад: газ, нафта, рента). УВАГА - ДІЮ НЕ МОЖНА БУДЕ ВІДМІНИТИ"  
        new_values = tas.lower().split(',')
        u = User()
        u.chat_id = list(Tags.handlers.keys())[-1]
        u.remove_tags(tag_name.lower().strip(), tags, new_values)
        u.changeScope('general')
        finish = yield f"Супер! Тепер при аналізі законопроекту я буду шукати в ньому ці ключові слова: {u.choose_tags(tag_name)}. Зараз можете спробувати ввести номер будь-якого законопроекту, наприклад 1122"
    elif quest == "3edit_tag":
        tas = yield f"Ого! Який саме набір треба видалити?. УВАГА - ДІЮ НЕ МОЖНА БУДЕ ВІДМІНИТИ"  
        u = User()
        u.chat_id = list(Tags.handlers.keys())[-1]
        print(f'tag_name = {tas.lower().strip()}, old_values = {tags}')
        u.remove_all(tas.lower().strip(), tags)
        u.changeScope('general')
        finish = yield f"Готово, набір видалено якісно"
    elif quest == "4edit_tag":
        u = User()
        u.chat_id = list(Tags.handlers.keys())[-1]
        u.changeScope('general')
        finish = yield 'Наступного разу вийде краще ))'

        





def check_tags():
    u = User()
    u.chat_id = list(Tags.handlers.keys())[-1]
    user_tags = u.getTags()
    if len(user_tags)==0:
        return True
    else:
        return False

class Tags(User, Update):
    handlers = defaultdict(dialog)

    def __init__(self, BOT_URL, data):
        self.BOT_URL = BOT_URL
        self.data = data
        self.start()
        print(self.message)
        print('start handle_tags')
        self.handle_tags()
        print('finish handle_tags')

    def handle_tags(self):
        print(self.handlers)
        print(f'my_messaage = {self.message}')
        if self.message == '/tags':
            # self.getTags()
            # self.select_tags()
            # self.changeScope('/tag')
            print(f'my_chat_id = {self.chat_id}')
            self.handlers.pop(self.chat_id, None)
            print(self.handlers)

        print(f'self_chat_id in handlers? = {self.chat_id in self.handlers}')

        if self.chat_id in self.handlers:
            
            try:
                answer = self.handlers[self.chat_id].send(self.message)
                if answer.find('Зараз в цьому наборі такі ключові слова:') >=0:
                    kb = json.dumps({ "inline_keyboard":[
                    [
                        { "text": "Додати теги", "callback_data": "1edit_tag" },
                        { "text": "Видалити теги", "callback_data": "2edit_tag" }
                    ],
                    [
                        { "text": "Видалити набір", "callback_data": "3edit_tag" },
                        { "text": "Вийти без змін", "callback_data": "4edit_tag" }
                    ]
                    ]})
                    json_data = {
                    "text": answer,
                    "chat_id" : self.chat_id,
                    "parse_mode": 'markdown',
                    'reply_markup': kb
                    }
                    self.send_message(json_data)
                else:
                    json_data = {
                    "text": answer,
                    "chat_id" : self.chat_id,
                    "parse_mode": 'markdown',
                    }
                    self.send_message(json_data)
            except StopIteration:
                # del self.handlers[self.chat_id]
                # return self.handle_tags()
                print(f'stop')
        else:
            answer = next(self.handlers[self.chat_id])

            if answer == 'У вас вже є набори тегів.':
                kb = json.dumps({ "inline_keyboard":[
                [
                    { "text": "Додати новий", "callback_data": "1choise_tag" },
                    { "text": "Редагувати", "callback_data": "2choise_tag" }
                ],
                [
                    { "text": "Я тут випадково", "callback_data": "3choise_tag" }
                ]
                ]})
                json_data = {
                "text": answer,
                "chat_id" : self.chat_id,
                "parse_mode": 'markdown',
                'reply_markup': kb
                }
                self.send_message(json_data)
                
            else: 
                json_data = {
                "text": answer,
                "chat_id" : self.chat_id,
                "parse_mode": 'markdown',
                }
                self.send_message(json_data)

    

    def new_tags(self, name, message):
        tags = message.split()
        di = {name:tags}
        self.tags.append(di)

    def choose_tags(self, name):
        try:
            for i in self.tags:
                if name in i.keys():
                    position = self.tags.index(i)
            my_tags = self.tags[position][name]
        except:
            my_tags = []

    def select_tags(self):
        print(len(self.tags))
        if len(self.tags) == 0:
            kb = json.dumps({ "inline_keyboard":[
                [
                    { "text": "Створити зараз", "callback_data": "1no_tag" },
                    { "text": "Створити пізніше", "callback_data": "2no_tag" }
                ]
                ]})
            json_data = {
            "text": "NO TAGS",
            "chat_id" : self.chat_id,
            "parse_mode": 'markdown',
            'reply_markup': kb
            }     
            print(self.chat_id)
            self.send_message(json_data)
        else:
            kb = json.dumps({ "inline_keyboard":self.tag_kb()})
            json_data = {
            "text": "CHOOSE TAGS",
            "chat_id" : self.chat_id,
            "parse_mode": 'markdown',
            'reply_markup': kb
            }     
            print(self.chat_id)
            self.send_message(json_data)

    def tag_kb(self):
        l = self.tags
        keyboard = []
        buttons = []
        while len(l)!=0:
            if len(buttons)<2:
                q = l.pop()
                di ={'text':q, 'callback_data':f'{len(l)}choose_tag'}
                buttons.append(di)
            else:
                keyboard.append(buttons)
                buttons = []
                q = l.pop()
                di ={'text':q, 'callback_data':f'{len(l)}choose_tag'}
                buttons.append(di)
        if len(buttons)!=0:
            keyboard.append(buttons)
            buttons = []
        return keyboard




# class Dialog_tag(Tags, Update):
#     def __init__(self, BOT_URL, data):
#         self.BOT_URL = BOT_URL
#         self.data = data
#         self.start()
#         self.get_tags(self.chat_id)
#         print(self.tags)

#         elif self.message == "1no_tag":
            
#         elif self.message == "2no_tag":
#             pass
#         elif self.message.find('_tag')>0:
#             pass

    




        


