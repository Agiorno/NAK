import requests
import json


class Update:

    BOT_URL = None
    last_message = 'restart'
    last_update_id = 0
    message = None
    
    def start(self):
        self.update_id = self.data['update_id']
        self.my_type = self.get_type(self.data)
        print(f'type =  = {self.my_type}')
        self.handle_message(self.data)
 
    def get_type(self, val):
        option = list(val.keys())[-1]
        return option
    
    def handle_message(self, val):
        try:
            if self.my_type == 'message':
                try:
                    self.message = self.data['message']['text']
                except:
                    self.message = 'mne prislali hernu'
                self.chat_id = self.data['message']['chat']['id']
                self.message_id = self.data['message']['message_id']
            elif self.my_type == 'callback_query':
                self.chat_id = self.data['callback_query']['message']['chat']['id']
                self.message = self.data['callback_query']['data']
                self.message_id = self.data['callback_query']['message']['message_id']
            elif self.my_type == 'edited_message':
                pass
            elif self.my_type == 'channel_post':
                pass
            elif self.my_type == 'edited_channel_post':
                pass
            elif self.my_type == 'inline_query':
                pass
            elif self.my_type == 'chosen_inline_result':
                pass 
            elif self.my_type == 'chat_member':
                pass
            elif self.my_type == 'shipping_query':
                pass
            elif self.my_type == 'pre_checkout_query':
                pass
            elif self.my_type == 'poll':
                pass
            elif self.my_type == 'poll_answer':
                pass
            elif self.my_type == 'my_chat_member':
                self.chat_id = self.data['my_chat_member']['chat']['id'] 
            else:
                self.my_type ='error'
        except KeyError:
            self.my_type ='error'
            
    def check_last(self, message):
        if self.my_type == 'error':
            pass
        else:
            if self.last_message == self.message:
                if self.last_message == 'restart':
                    self.send_message(self.just_text('restart succeed'))
                else:
                    self.last_message = self.message
            if self.last_update_id != self.update_id:
                self.last_update_id = self.update_id
                self.query = 'new_query'
            else:
                self.query = 'repeated_query'
            
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
        
    def just_text(self, text, chat=None):
        if chat:

            json_data = {
                "chat_id": chat,
                "text": text
            }
        else:
            json_data = {
                "chat_id": self.chat_id,
                "text": text
            }
        return json_data
