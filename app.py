import requests
from bottle import Bottle, response, request as bottle_request
from nak_bill_analize import NAK
from bothandler import BotHandler
import ast

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

    def post_handler(self):
        
        self.data = bottle_request.json
        self.handle_data()
        nak = NAK(self.data)
        nak.BOT_URL = self.BOT_URL
        nak.bot_analize_bills_for_nak()
        



if __name__ == '__main__':  
    app = TelegramBot()
    app.run(host='localhost', port=8080)
