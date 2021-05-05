import requests
from bottle import Bottle, response, request as bottle_request
from update import Update
from keywords import KeyWords
import ast
import ninox_log as nl
from login import Login
from answer import AnswerMethod

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
    

class TelegramBot(Update, Bottle):  
    
    updated_id = []
    BOT_URL = bot['BOT_URL']
    

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
        self.start()
            
        print(f'Это новый запрос? : {self.update_id not in self.updated_id}')
        if self.update_id not in self.updated_id:
            log = Login(self.BOT_URL, self.data)
            print(log.status)
            if log.status:
                if self.message:
                    print(f"текст сообщения: {self.message}. Ушло на проверку ключевых слов.")
                    a = KeyWords(self.BOT_URL, self.data)
                else:
                    print(f"текст сообщения отсутсвует")
                self.updated_id.append(self.update_id)      
        else:
            pass




        

            



if __name__ == '__main__':  
    app = TelegramBot()
    app.run(host='localhost', port=8080)
