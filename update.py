import requests
import json


class Update:

    BOT_URL = None
    last_message = 'restart'
    last_update_id = 0
    message = None
    
    def start_update(self):
        self.update_id = self.data['update_id']
        self.my_type = self.get_type(self.data)
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
                self.is_bot  = self.data['message']['from']['is_bot']
                try:
                    self.first_name = self.data['message']['from']['first_name']
                except:
                    self.first_name = ''
                try:
                    self.last_name = self.data['message']['from']['last_name']
                except:
                    self.last_name = ''
                try:
                    self.user_name = self.data['message']['from']['user_name']
                except:
                    self.user_name = ''
            elif self.my_type == 'callback_query':
                self.chat_id = self.data['callback_query']['message']['chat']['id']
                self.message = self.data['callback_query']['data']
                self.message_id = self.data['callback_query']['message']['message_id']
            elif self.my_type == 'edited_message':
                pass
            elif self.my_type == 'channel_post':
                self.message_id = self.data['channel_post']['message_id']
                self.chat_id = self.data['channel_post']['sender_chat']['id']

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
                self.from_id = self.data['my_chat_member']['from']['id']
                self.old_status = self.data['my_chat_member']['old_chat_member']['status']
                self.old_user_id = self.data['my_chat_member']['old_chat_member']['user']['id']
                self.new_status = self.data['my_chat_member']['new_chat_member']['status']
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

    def leave_chat(self, prepared_data=None):
        message_url = self.BOT_URL+'leaveChat'
        if not prepared_data:
            prepared_data = {
                'chat_id':self.chat_id
            }
        self.response = requests.post(message_url, prepared_data)
        
    def edit_reply(self, message_id = None, chat_id = None):
        if not message_id:
            message_id = self.message_id
        if not chat_id:
            chat_id = self.chat_id
        message_url = self.BOT_URL + 'editMessageReplyMarkup'
        kb = json.dumps({ "inline_keyboard":[[]]})
        json_data = {
            "message_id": message_id,
            "chat_id" : chat_id,
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
