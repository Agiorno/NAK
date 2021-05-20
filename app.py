from users import User
import requests
from bottle import Bottle, response, request as bottle_request
from update import Update
from keywords import KeyWords
import ast
import ninox_log as nl

from login import Login
from answer import AnswerMethod
from pymongo import MongoClient
from nak import NAK

with open("monkey", "r") as f:
    bot = ast.literal_eval(f.read())

ngrok = bot['ngrok']
set_webhook = f"{bot['BOT_URL']}setWebHook?url={ngrok}]"
getWebhookInfo = f"{bot['BOT_URL']}getWebhookInfo"
delete_webhook = f"{bot['BOT_URL']}deleteWebhook"
r = requests.get(getWebhookInfo).json()
print(r)
if r['result']['url'] == '':
    requests.get(delete_webhook)
    requests.get(set_webhook)
    print(r)
    

class TelegramBot(Update, Login, KeyWords, User,  NAK, Bottle):  
    
    updated_id = []
    BOT_URL = bot['BOT_URL']
    client = MongoClient(bot['mongo'])
    db = client.Rada
    log = db.Log
    users = db.BOT
    user = None

    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__()
        self.route('/', callback=self.post_handler, method="POST")


    def send_log(self):
        dogs=[]
        di = {'fields':{'data':str(self.data)}}
        dogs.append(di)
        nl.n.send_to_ninox(dogs, nl.my_schema['requests'])




    
    def post_handler(self):
        print('пришло сообщение')
        self.data = bottle_request.json
        self.send_log()
        self.start_update()
            
        print(f'Это новый запрос? : {self.update_id not in self.updated_id}')
        if self.update_id not in self.updated_id:
            self.check_login()
            if self.status:
                if self.message:
                    print(f"текст сообщения: {self.message}. Ушло на проверку ключевых слов.")
                    self.check_keywords()
                else:
                    print(f"текст сообщения отсутсвует")
                self.updated_id.append(self.update_id)      
        else:
            pass
        print(5)
        print(self.data)
        print(f'user = {self.user}')



        

            



if __name__ == '__main__':  
    app = TelegramBot()
    app.run(host='localhost', port=8080)
