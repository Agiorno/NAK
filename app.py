import requests
from bottle import Bottle, response, request as bottle_request
from nak_bill_analize import NAK
from check_updates import CheckNewBills
from bothandler import BotHandler
import ast
import sys
import os

with open("monkey", "r") as f:
    bot = ast.literal_eval(f.read())

class TelegramBot(BotHandler, Bottle):  
   
    BOT_URL = bot['BOT_URL']
    

    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__()
        self.route('/', callback=self.post_handler, method="POST")

    
    def just_text(self, text):
        json_data = {
            "chat_id": self.chat_id,
            "text": text
        }
        return json_data


    def restart(self):

        print("argv was",sys.argv)
        print("sys.executable was", sys.executable)
        os.execv(sys.executable, ['python'] + sys.argv)		
    
    def post_handler(self):
        
        self.data = bottle_request.json
        self.handle_data()
        if self.message == 'restart':
            self.send_message(self.just_text('сервер перезагружается, подождите'))
            print(f'message = {self.message}')
            print(f'last_ message = {self.last_message}')
            self.restart()
        elif self.message == 'restart succeed':
            self.send_message(self.just_text('перезагрузка сервера прошла успешно'))
        elif self.message == 'mne prislali hernu':
            self.send_message(self.just_text('Шановні колеги, не балуйтесь. Які стікери?! Ви шо!! Використовуйте мене за призначенням'))
        elif self.message == 'photophoto':
            domain = 'https://esp.ngrok.io/'
            file_name = '4050_table.png'
            file_path = domain+file_name
            message = f'{self.BOT_URL}sendPhoto'
            # message_url = self.BOT_URL + 'sendMessage'
            # self.response = requests.post(message_url, json=prepared_data)
            json_data = {
                "chat_id": self.chat_id,
                "caption": "4550",
                "photo": file_path
            }

            sssend = requests.post(message, json = json_data)
        elif self.message == 'update bills':
            c = CheckNewBills()
            message = c.check_everything()
            self.send_message(self.just_text(message))
        else:
            nak = NAK(self.data)
            nak.BOT_URL = self.BOT_URL
            nak.bot_analize_bills_for_nak()
            



if __name__ == '__main__':  
    app = TelegramBot()
    app.run(host='localhost', port=8080)
