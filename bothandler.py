import requests
import json

class BotHandler:  
    BOT_URL = None
    last_message = 'restart'
    
    def handle_data(self):
        try:
            self.chat_id = self.data['message']['chat']['id']
            self.message = self.data['message']['text']
            if self.last_message == self.message:
                if self.last_message == 'restart':
                    self.message = 'restart succeed'
                    
            else:
                self.last_message = self.message

            self.message_id = self.data['message']['message_id']
            self._type = 'message'
           
        except KeyError:
            self.chat_id = self.data['callback_query']['message']['chat']['id']
            self.message = self.data['callback_query']['data']
            self.message_id = self.data['callback_query']['message']['message_id']
            self._type = 'callback_query'
    
    def send_message(self, prepared_data):
        message_url = self.BOT_URL + 'sendMessage'
        self.response = requests.post(message_url, json=prepared_data)
        
        
    def edit_reply(self):
        message_url = self.BOT_URL + 'editMessageReplyMarkup'
        kb = json.dumps({ "inline_keyboard":[[]]})
        json_data = {
            "message_id": self.message_id,
            "chat_id" : self.chat_id,
            'reply_markup': kb
            }
        requests.post(message_url, json=json_data)
        
    def just_text(self, text):
        json_data = {
            "chat_id": self.chat_id,
            "text": text
        }
        return json_data