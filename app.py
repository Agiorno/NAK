import requests
from bottle import Bottle, response, request as bottle_request
from nak_bill_analize import NAK
from check_updates import CheckNewBills
from update import Update
from keywords import KeyWords
import ast


with open("monkey", "r") as f:
    bot = ast.literal_eval(f.read())

class TelegramBot(Update, Bottle):  
   
    BOT_URL = bot['BOT_URL']
    

    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__()
        self.route('/', callback=self.post_handler, method="POST")


    
    def post_handler(self):
        print('get_data')
        self.data = bottle_request.json
        self.start()
        print('send data to Upload')
        if self.message:
            print(self.message)
            a = KeyWords(self.BOT_URL, self.data)
        else:
            print(self.message)



        

            



if __name__ == '__main__':  
    app = TelegramBot()
    app.run(host='localhost', port=8080)
