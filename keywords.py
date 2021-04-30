from update import Update 
from nak import NAK
import sys
import os
from datetime import datetime
from check_updates import CheckNewBills 
import time
 
 
class KeyWords(Update): 
    now = datetime.now()
    timestamp = round(datetime.timestamp(now))

    def __init__(self, bot_url, data):
        self.data = data
        self.start()
        self.BOT_URL = bot_url
        if self.update_id != self.last_update_id:

            self.last_update_id = self.update_id
            if self.message == 'restart':
                self.restart()
            elif self.message == 'mne prislali hernu':
                self.hernia()
            elif self.message == 'update bills':
                self.update_bills()
            elif self.message == 'photophoto':
                self.photo()
            else:
                    self.nak()
        else:
            pass


    
    def restart(self):
        if self.timestamp > self.data['message']['date']:
            if self.message == 'restart':
                self.send_message(self.just_text('перезагрузка сервера прошла успешно'))
        else:
            self.send_message(self.just_text('сервер перезагружается, подождите'))
            print("argv was",sys.argv)
            print("sys.executable was", sys.executable)
            os.execv(sys.executable, ['python'] + sys.argv)		
    
    def hernia(self):
        self.send_message(self.just_text('Шановні колеги, не балуйтесь. Які стікери?! Ви шо!! Використовуйте мене за призначенням'))

    def update_bills(self):
        self.send_message(self.just_text('починаемо перевірку нових законопроектів'))
        c = CheckNewBills()
        message = c.check_everything()
        self.send_message(self.just_text(message))
    
    def nak(self):    
        nak = NAK(self.BOT_URL, self.data)
    
    def photo(self):
 
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
        requests.post(message, json = json_data)