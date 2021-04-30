from ninox_log import send_log
from upload_bills import get_links, send_info, Bills
import json  
from answer import Answer, AnswerMethod
from update import Update

class NAK(Update):
    
    def __init__(self, bot_url, data):
        self.BOT_URL = bot_url #забрали ссылку на бота
        self.data = data  #забрали входящий json
        self.start()  #запустили парсинг json (Update.start)
        self.bot_analize_bills_for_nak() #вернули ответ
        

    
    #CRM answer
    def generate_keyboard(self, bill, my_answer):
        
        if str(self.message) in bill.list_of_bills:
            self.text = bill.check_info(str(self.message))
            self.kb = AnswerMethod().make_inline_keyboard(empty=True)
        else:
            self.text = "Цей законопроект відсутній в базі" 
            self.kb=AnswerMethod().make_inline_keyboard(option1 = { "text": "Додати", "callback_data": "1" },
                                              option2 = { "text": "Не додавати", "callback_data": "2" })
        my_message = f'''{my_answer}

📍 *CRM*: {self.text}''' 

        return my_message
    
    #  Суть: вытащить ссылку на законопроект из оригинального сообщения, под которым появились кнопкы.
    #  в запросе могут находится две ссылки - одна на страницу законопроекта 
    #  - короткая, вторая на документ - длинная. Нам нужна короткая. 
    def get_url(self):
        url = ''
        for i in self.data['callback_query']['message']['entities']:
            if 'url' in i.keys():
                if url == '':
                    url = i['url']
                else:
                    if len(i['url'])<len(url):
                        url = i['url']
        return url

    def prepare_data_for_answer(self, link):

        self.bill = Bills() # обновили список законопроектов
        
        m = Answer(link) # сфорировали текст обратного ответа, на основе ссылки на законопроект в Раде
        my_answer = m.my_message
        self.my_answer = self.generate_keyboard(self.bill, my_answer) # подвезали к тексту клавиатуру, если нужно

        send_log(self.data, self.my_answer, m.law_name, m.law_number, link) # отправили в нинокс лог(запрос-ответ)
        
        json_data = {
            "chat_id": self.chat_id,
            "text": self.my_answer,
            "reply_to_message_id": self.message_id,
            "parse_mode": 'markdown',
            'reply_markup': self.kb
        }

        return json_data
    
    
    def bot_analize_bills_for_nak(self):
        
        # проверка, чтоб текст сообщения был сам по себе и был не меньше четырех символов
        if  self.my_type == 'message':
            if len(self.message)>3:
                # если да, то формирум список ссылок на связанные законопроекты
                array = get_links(self.message)
                # и если список пуст - значит такого законопроекта не существует
                if len(array)==0:
                    self.send_message(self.just_text(AnswerMethod().wrong_request()))
                # а если в списке есть хоть одна ссылка, 
                 
                else:
                    # то для каждой ссылки готовим ответ и отправляем его отправителю
                    for i in array:
                        answer_data = self.prepare_data_for_answer(i)
                        self.send_message(answer_data)
                        print('[НАК]: СООБЩЕНИЕ ОТПРАВЛЕНО УСПЕШНО')
            # а если в тексте меньше четырех символов или вообще нет сообщения, то посылаем
            else:
                self.send_message(self.just_text(AnswerMethod().wrong_request()))

        # а если, это не сообщение, а ответ на кнопку
        elif self.my_type == 'callback_query':
            # то в первом случае пробуем выполняем первое действие, во втором второе итд
            try:
                # согласились
                if self.message == "1":
                    url = self.get_url()
                    send_info(url)
                    self.send_message(self.just_text('Законопроект доданий до CRM в розділ *Bills* (Постійний моніторинг).'))
                    self.bill = Bills()
                # отказались
                else:
                    self.send_message(self.just_text('Законопроект не включений до постійного моніторінгу'))
                
                # после чего удаляем клавиатуру
                self.edit_reply()
                print('[НАК]: КЛАВИАТУРА УДАЛЕНА')
                self.bill = Bills()
            
            # если что-то пошло не так - например, это ответ не на нашу кнопку, то посылаем
            except KeyError:

                 self.send_message(self.just_text(AnswerMethod().wrong_request()))
        # если это и не сообщение и не ответ на кнопку - до свидания!           
        else:
            pass