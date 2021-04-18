import requests
import os
import urllib.parse
from analizator import Analizator, get_links, get_atrrs
from bottle import Bottle, response, request as bottle_request
from ninox_log import send_log
from upload_bills import get_links, send_info, Bills
import json
from importlib import reload  


class BotHandlerMixin:  
    BOT_URL = None
   
    
    def is_it_callback(self, data):
        try:
            self.chat_id = data['message']['chat']['id']
            self.message = data['message']['text']
            self.message_id = data['message']['message_id']
            self._type = 'message'
           
        except KeyError:
            self.chat_id = data['callback_query']['message']['chat']['id']
            self.message = data['callback_query']['data']
            self.message_id = data['callback_query']['message']['message_id']
            self._type = 'callback_query'
        
        return self._type

    def get_chat_id(self, data):
        """
        Method to extract chat id from telegram request.
        """
        chat_id = data['message']['chat']['id']

        return chat_id

    def get_message(self, data):
        """
        Method to extract message id from telegram request.
        """
        message_text = data['message']['text']

        return message_text
    
    def send2(self, prepared_data):
        message_url = self.BOT_URL + 'sendMessage'
        self.response = requests.post(message_url, json=prepared_data)
        
        
    def edit_reply(self, data):
        message_url = self.BOT_URL + 'editMessageReplyMarkup'
        requests.post(message_url, json=data)


class TelegramBot(BotHandlerMixin, Bottle):  
   
    BOT_URL = 'https://api.telegram.org/bot1200141862:AAE3YD6hY9GJBJ5o8JU-GjKn570vujltz1k/'
    counter = 0
    

    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__()
        self.route('/', callback=self.post_handler, method="POST")
        TelegramBot.counter +=1

    def prepare_data_for_answer(self, message, chat_id, link, data):
        
        self.bill = Bills()
        answer = Analizator(link, 'tags')
        
        law_number = get_atrrs(link)[1]
       
        law_name = get_atrrs(link)[0]
       
        info_message = f'''✏️ *Назва*: {law_name}
        
📑 *Номер*:  🔗[{law_number}]({link})

'''
        
        print(answer.status)
        if answer.status == 'ok':
            if len(answer.result)==0:
                os.remove('text.docx')
                my_message = f"""{info_message} 
*Аналіз тегів*: ✅ У законопроекті відсутні ключові слова"""
                
            else:
                os.rename('text.docx', f'b{self.counter}.docx')
                my_message = f"""{info_message} 
*Аналіз тегів*: ❗️❗️❗️  У законопроекті знайдені ключові слова: """
                for i in answer.result:
                    my_message = f'{my_message}{i} '
                self.counter +=1

        elif answer.status == 'error':
            my_message = f"""{info_message} 
*Аналіз тегів*: 🚫 У законопроекті відсутній текст для аналізу"""
            
        elif answer.status == 'rtf':
            
            my_message = f"""{info_message} 
*Аналіз тегів*: ❌ Знайдено текст, проте бот _не може_ аналізувати .rtf файли. [Передивіться особисто.]({answer.file_link})"""
            
        elif answer.status == 'pdf':
            
            my_message = f"""{info_message} 
*Аналіз тегів*: ❌ Знайдено текст, проте бот _не може_ аналізувати .pdf файли. [Передивіться особисто.]({answer.file_link})"""
           
        else:
            my_message = f"""{info_message} 
*Аналіз тегів*: ❌ Неможливо опрацювати текст законопроекту. [Перевірте особисто]({answer.file_link})"""
          
        if str(message) in self.bill.list_of_bills:
            self.text = self.bill.check_info(str(message))
            self.kb = json.dumps({ "inline_keyboard":[[]]})
        else:
            self.text = "Цей законопроект відсутній в базі" 
            
        
            
            self.kb=json.dumps(
                { "inline_keyboard":
                    [
                        [
                            { "text": "Додати", "callback_data": "1" },
                            { "text": "Не додавати", "callback_data": "2" }
                        ]
                    ]
                }
            )
            
        my_message = f'''{my_message}
        
📍 *CRM*: {self.text}'''   
        print(send_log(data, my_message, law_name, law_number, link))
        
        return my_message
    

    def prepare_data_for_answer1(self, data, link):
        message = self.get_message(data)
        chat_id = self.get_chat_id(data)
        answer = self.prepare_data_for_answer(message, chat_id, link, data)
        
        print(answer)
        json_data = {
            "chat_id": chat_id,
            "text": answer,
            "reply_to_message_id": self.message_id,
            "parse_mode": 'markdown',
            'reply_markup': self.kb
        }
       

        return json_data
    
    def just_text(self, text):
        json_data = {
            "chat_id": self.chat_id,
            "text": text
        }
        return json_data

    def post_handler(self):
        
        data = bottle_request.json
#         message = self.get_message(data)
#         chat_id = self.get_chat_id(data)
        _type = self.is_it_callback(data)
        if  _type == 'message':
            array = get_links(self.message)
            print(array)
            if len(array)==0:
                self.send2(self.just_text('НЕКОРЕКТНИЙ ЗАПИТ'))
            else:
                for i in array:
                    print(i)
                    answer_data = self.prepare_data_for_answer1(data, i)
                    self.send2(answer_data)
                    print(self.response.json())
                    print('message has sent')
                    
                      
                   
        else:
            
            if self.message == "1":
                
#                 print(self.response.json())
#                 print(data)
                url = ''
                for i in data['callback_query']['message']['entities']:
                    if 'url' in i.keys():
                        if url == '':
                            url = i['url']
                        else:
                            if len(i['url'])<len(url):
                                url = i['url']
                send_info(url)
                self.send2(self.just_text('Законопроект доданий до CRM в розділ *Bills* (Постійний моніторинг).'))
                self.bill = Bills()
              
                
                
                 
            else:
                self.send2(self.just_text('OK'))
                print(data)
                print(self.response.json())
                
            kb = json.dumps({ "inline_keyboard":[[]]})
            json_data = {
                "message_id": self.message_id,
                "chat_id" : self.chat_id,
                'reply_markup': kb
                }
            self.edit_reply(json_data)
            print('keyboard has removed')
            self.bill = Bills()
            
                      
        
              
                    





if __name__ == '__main__':  
    app = TelegramBot()
    app.run(host='localhost', port=8080)